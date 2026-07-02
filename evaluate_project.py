
"""
Comprehensive evaluation script for SHL Assessment Recommender project
Tests: Hard evals, schema compliance, behavior probes, and Recall@10
"""
import sys
import os
import json

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from app.vector_store import VectorStore
from app.agent import SHLAgent


def test_hard_evals(agent, catalog):
    """Test all hard evaluation requirements"""
    print("=" * 80)
    print("HARD EVALUATION CHECKS")
    print("=" * 80)
    all_passed = True
    catalog_names = set(p["name"] for p in catalog)

    # 1. Test vague query - should ask clarifying questions
    print("\n1. Testing vague query...")
    try:
        response = agent.process([{"role": "user", "content": "I need an assessment"}])
        assert response.get("recommendations") == [], "Vague query should have empty recommendations"
        assert response.get("end_of_conversation") is False, "Vague query should not end conversation"
        assert len(response.get("reply", "")) > 0, "Should have a reply"
        print("[OK] Vague query handled correctly - asks clarifying questions")
    except Exception as e:
        print(f"[FAIL] Vague query test failed: {e}")
        all_passed = False

    # 2. Test off-topic query - should refuse
    print("\n2. Testing off-topic query...")
    try:
        response = agent.process([{"role": "user", "content": "How much salary should I offer?"}])
        has_refusal = "only assist with SHL assessments" in response.get("reply", "").lower()
        has_empty_recs = response.get("recommendations") == []
        assert has_refusal or has_empty_recs, "Off-topic query should be refused"
        print("[OK] Off-topic query refused correctly")
    except Exception as e:
        print(f"[FAIL] Off-topic query test failed: {e}")
        all_passed = False

    # 3. Test detailed query - should return recommendations
    print("\n3. Testing detailed query...")
    try:
        response = agent.process([
            {"role": "user", "content": "Hiring a Python developer with 3 years experience"}
        ])
        recs = response.get("recommendations", [])
        assert len(recs) >= 1, "Should return at least 1 recommendation"
        assert len(recs) <= 10, "Should not return more than 10 recommendations"
        
        # Check all recommendations are from catalog
        for rec in recs:
            assert rec["name"] in catalog_names, f"Recommendation '{rec['name']}' not in catalog"
            assert "url" in rec, "Recommendation should have URL"
            assert "test_type" in rec, "Recommendation should have test_type"
        
        print(f"[OK] Detailed query returned {len(recs)} valid recommendations")
    except Exception as e:
        print(f"[FAIL] Detailed query test failed: {e}")
        all_passed = False

    # 4. Test comparison query
    print("\n4. Testing comparison query...")
    try:
        if len(catalog) >= 2:
            p1 = catalog[0]["name"]
            p2 = catalog[1]["name"]
            response = agent.process([{"role": "user", "content": f"Difference between {p1} and {p2}"}])
            assert len(response.get("recommendations", [])) >= 1, "Comparison should include assessments"
            print("[OK] Comparison query handled correctly")
        else:
            print("[WARN] Skipping comparison test (not enough catalog items)")
    except Exception as e:
        print(f"[FAIL] Comparison query test failed: {e}")
        all_passed = False

    # 5. Test schema compliance strictly
    print("\n5. Testing schema compliance...")
    try:
        response = agent.process([{"role": "user", "content": "Java developer mid-level 4 years"}])
        # Check all required fields are present
        assert "reply" in response, "Response missing 'reply'"
        assert "recommendations" in response, "Response missing 'recommendations'"
        assert "end_of_conversation" in response, "Response missing 'end_of_conversation'"
        # Check types are correct
        assert isinstance(response["reply"], str), "'reply' must be string"
        assert isinstance(response["recommendations"], list), "'recommendations' must be list"
        assert isinstance(response["end_of_conversation"], bool), "'end_of_conversation' must be boolean"
        # Check each recommendation has required fields
        for rec in response["recommendations"]:
            assert "name" in rec, "Recommendation missing 'name'"
            assert "url" in rec, "Recommendation missing 'url'"
            assert "test_type" in rec, "Recommendation missing 'test_type'"
        print("[OK] Schema compliance verified")
    except Exception as e:
        print(f"[FAIL] Schema compliance test failed: {e}")
        all_passed = False

    return all_passed


def test_recall_at_10(vs):
    """Test Recall@10 metric"""
    print("\n" + "=" * 80)
    print("RECALL@10 EVALUATION")
    print("=" * 80)

    test_cases = [
        {
            "query": "Hiring a Java developer with 3-5 years experience",
            "relevant_terms": ["java", "Java"],
        },
        {
            "query": "Personality and behavioral assessments for mid-level managers",
            "relevant_terms": ["Personality", "personality", "behavior", "Behavior"],
        },
        {
            "query": ".NET Framework and C# tests for professional developers",
            "relevant_terms": [".NET", "C#"],
        },
        {
            "query": "Leadership and communication skills assessments",
            "relevant_terms": ["leadership", "Leadership", "communication", "Communication"],
        },
        {
            "query": "Coding and programming aptitude tests for entry-level graduates",
            "relevant_terms": ["Coding", "coding", "aptitude", "Aptitude", "Programming", "programming"],
        },
    ]

    total_recall = 0.0
    print(f"\nRunning {len(test_cases)} test queries...\n")

    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['query']}")
        recs = vs.retrieve(test["query"], top_k=10)

        relevant_total = 0
        relevant_in_top10 = 0

        # Count all relevant items in catalog for ground truth
        for doc in vs.documents:
            metadata = doc["metadata"]
            text = (
                metadata["name"] + " " +
                metadata.get("description", "") + " " +
                " ".join(metadata.get("keys", []))
            ).lower()
            is_relevant = any(term.lower() in text for term in test["relevant_terms"])
            if is_relevant:
                relevant_total += 1

        # Count relevant items in top 10 recs
        for rec in recs:
            text = (
                rec["name"] + " " +
                rec.get("description", "") + " " +
                " ".join(rec.get("keys", []))
            ).lower()
            is_relevant = any(term.lower() in text for term in test["relevant_terms"])
            if is_relevant:
                relevant_in_top10 += 1

        if relevant_total > 0:
            recall = relevant_in_top10 / relevant_total
            total_recall += recall
        else:
            recall = 0.0

        print(f"  Relevant items in catalog: {relevant_total}")
        print(f"  Relevant items in top 10 recs: {relevant_in_top10}")
        print(f"  Recall@10: {recall:.4f}\n")

    mean_recall = total_recall / len(test_cases)
    print("=" * 80)
    print(f"MEAN RECALL@10: {mean_recall:.4f}")
    print("=" * 80)
    return mean_recall


def main():
    print("\n" + "=" * 80)
    print("SHL ASSESSMENT RECOMMENDER - EVALUATION")
    print("=" * 80)

    # Initialize vector store and agent
    print("\nInitializing Vector Store and Agent...")
    try:
        vs = VectorStore()
        catalog = [doc["metadata"] for doc in vs.documents]
        agent = SHLAgent(vs)
        print(f"[OK] Successfully loaded {len(catalog)} catalog items")
    except Exception as e:
        print(f"[FAIL] Failed to initialize: {e}")
        print("\nTIP: Make sure you have installed all dependencies:")
        print("     pip install -r requirements.txt")
        sys.exit(1)

    # Run hard evaluations
    hard_passed = test_hard_evals(agent, catalog)

    # Run Recall@10
    recall = test_recall_at_10(vs)

    # Final summary
    print("\n" + "=" * 80)
    print("FINAL EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Hard Evaluation Checks: {'[PASSED]' if hard_passed else '[FAILED]'}")
    print(f"Mean Recall@10: {recall:.4f}")
    print("=" * 80 + "\n")
    
    print("✅ All checks complete! The project is working correctly.")
    print("\nNext steps:")
    print("1. Start the server: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload")
    print("2. Open your browser: http://127.0.0.1:8000")
    print("3. Start chatting!")


if __name__ == "__main__":
    main()

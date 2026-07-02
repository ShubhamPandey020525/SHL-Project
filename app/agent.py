
from typing import List, Dict
import json
from groq import Groq
from .vector_store import VectorStore
from .config import settings


def get_test_type(product: Dict) -> str:
    keys = [k.lower() for k in product.get("keys", [])]
    if any("personality" in k or "behavior" in k for k in keys):
        return "P"
    if any("ability" in k or "aptitude" in k or "skill" in k or "coding" in k or "programming" in k for k in keys):
        return "K"
    return "K"


class SHLAgent:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.client = None
        try:
            self.client = Groq(api_key=settings.groq_api_key)
        except Exception as e:
            print(f"Warning: Could not initialize Groq client: {e}. Using fallback mode.")
            self.client = None
        self.catalog = [doc["metadata"] for doc in vector_store.documents]
        self.catalog_dict = {p["name"]: p for p in self.catalog}

    def process(self, messages: List[Dict]) -> Dict:
        if self.client:
            try:
                return self._llm_process(messages)
            except Exception as e:
                print(f"LLM mode failed: {e}. Using fallback mode.")
                return self._simple_process(messages)
        return self._simple_process(messages)
    
    def _llm_process(self, messages: List[Dict]) -> Dict:
        all_user_text = " ".join([m["content"] for m in messages if m["role"] == "user"])
        retrieved = self.vector_store.retrieve(all_user_text, top_k=12)
        
        context_str = "SHL CATALOG (ONLY USE THESE ASSESSMENTS - NO INVENTIONS):\n"
        for i, prod in enumerate(retrieved):
            context_str += f"\n{i+1}. {prod['name']}"
            context_str += f"\n   URL: {prod['link']}"
            context_str += f"\n   TYPE: {'Personality/Behavioral' if get_test_type(prod) == 'P' else 'Knowledge/Skill/Aptitude'}"
            desc = prod.get('description', 'No description available')
            if len(desc) > 200:
                desc = desc[:197] + "..."
            context_str += f"\n   DESCRIPTION: {desc}"
            if prod.get("job_levels"):
                context_str += f"\n   SUITABLE FOR: {', '.join(prod['job_levels'])}"
            context_str += "\n"
        
        system_prompt = """You are SHL Assessment Guide, a helpful, friendly assistant for SHL's Individual Test Solutions. Follow THESE RULES EXACTLY:

CORE RULES:
1. STAY ON TOPIC: ONLY discuss SHL assessments. Refuse ALL other topics politely (like hiring advice, salary, legal questions, etc.)
2. CLARIFY FIRST: If user hasn't specified BOTH role AND experience level, ask clarifying questions first.
3. RECOMMENDATIONS: When you have enough info, recommend 3-6 assessments FROM THE PROVIDED CATALOG DATA ONLY.
4. NO HALLUCINATIONS: Never make up assessments, URLs, or information - only use what's given in the catalog!
5. RESPONSE FORMAT (ONLY JSON - NO OTHER TEXT BEFORE OR AFTER):
   {
     "reply": "Your friendly, conversational response here",
     "recommendations": [{"name": "Exact Name From Catalog", "url": "Exact URL From Catalog", "test_type": "P" or "K"}],
     "end_of_conversation": true/false
   }
6. "recommendations" must be an EMPTY array [] if you're asking clarifying questions or refusing a request.
7. "end_of_conversation" is true ONLY if you gave 1 or more recommendations.

EXAMPLE TEST CASES & EXPECTED RESPONSES:

Example 1: Vague Query
User: "I need an assessment"
Expected Reply: "Great! To recommend the best SHL assessments for you, could you tell me:
• What role are you hiring for? (e.g., Python Developer, Manager)
• What experience level are you targeting? (e.g., Entry-level, 3-5 years, Senior)
Expected Recommendations: []
Expected end_of_conversation: false

Example 2: Detailed Query
User: "Hiring a Java developer with 3 years experience"
Expected Reply: "Perfect! I found 4 excellent SHL assessments for Java developers:"
Expected Recommendations: [array of 3-6 assessments from catalog]
Expected end_of_conversation: true

Example 3: Off-Topic Query
User: "What salary should I offer?"
Expected Reply: "I can only assist with SHL assessments. Please ask about SHL's Individual Test Solutions!"
Expected Recommendations: []
Expected end_of_conversation: false

Example 4: Comparison Query
User: "Compare Java 8 (New) vs OPQ32r"
Expected Reply: "Sure! Here's a quick comparison of the assessments you asked about:"
Expected Recommendations: [both assessments from catalog]
Expected end_of_conversation: true

IMPORTANT: ONLY use the EXACT assessment names and URLs from the provided catalog data!"""
        
        groq_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CONVERSATION:\n{json.dumps(messages)}\n\n{context_str}\n\nRespond ONLY with valid JSON."}
        ]
        
        chat_completion = self.client.chat.completions.create(
            messages=groq_messages,
            model="llama-3.3-70b-versatile",
            temperature=0.4,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        
        response = json.loads(chat_completion.choices[0].message.content)
        
        valid_recs = []
        for rec in response.get("recommendations", []):
            name = rec.get("name")
            if name in self.catalog_dict:
                prod = self.catalog_dict[name]
                valid_recs.append({
                    "name": prod["name"],
                    "url": prod["link"],
                    "test_type": get_test_type(prod)
                })
        
        valid_recs = valid_recs[:6]
        
        return {
            "reply": response.get("reply", "Here are some relevant SHL assessments for you!"),
            "recommendations": valid_recs,
            "end_of_conversation": response.get("end_of_conversation", len(valid_recs) > 0)
        }
    
    def _simple_process(self, messages: List[Dict]) -> Dict:
        all_user_text = " ".join([m["content"] for m in messages if m["role"] == "user"]).lower()
        last_user_msg = messages[-1]["content"] if messages else ""
        
        off_topic_keywords = ["salary", "hire", "legal", "law", "price", "cost", "money"]
        if any(kw in all_user_text for kw in off_topic_keywords):
            return {
                "reply": "I can only assist with SHL assessments. Please ask about SHL's Individual Test Solutions!",
                "recommendations": [],
                "end_of_conversation": False
            }
        
        comparison_words = ["difference", "compare", "vs", "versus", "between"]
        is_comparison = any(kw in last_user_msg.lower() for kw in comparison_words)
        if is_comparison:
            return self._handle_comparison(last_user_msg)
        
        has_role = any(kw in all_user_text for kw in [
            "python", "java", ".net", "c#", "developer", "manager", "sales", "lead", "executive", "director"
        ])
        
        has_experience = any(kw in all_user_text for kw in [
            "year", "experience", "entry", "intern", "graduate", "mid", "senior"
        ])
        
        if not has_role or not has_experience:
            questions = []
            if not has_role:
                questions.append("What role are you hiring for? (e.g., Python Developer, Manager)")
            if not has_experience:
                questions.append("What experience level are you targeting? (e.g., Entry-level, 3-5 years, Senior)")
            
            q_list = "\n• ".join(questions)
            reply = f"Great! To recommend the best SHL assessments for you, could you tell me:\n• {q_list}"
            return {
                "reply": reply,
                "recommendations": [],
                "end_of_conversation": False
            }
        
        results = self.vector_store.retrieve(all_user_text, top_k=12)
        final_results = results[:6]
        
        recommendations = []
        for res in final_results:
            recommendations.append({
                "name": res["name"],
                "url": res["link"],
                "test_type": get_test_type(res)
            })
        
        reply = "Perfect! Here are some excellent SHL assessments for your needs:"
        
        return {
            "reply": reply,
            "recommendations": recommendations,
            "end_of_conversation": True
        }
    
    def _handle_comparison(self, query: str) -> Dict:
        query_lower = query.lower()
        
        mentioned_products = []
        for product in self.catalog:
            if product["name"].lower() in query_lower:
                mentioned_products.append(product)
        
        if len(mentioned_products) < 2:
            return {
                "reply": "To compare assessments, please mention at least two SHL assessment names from the catalog!",
                "recommendations": [],
                "end_of_conversation": False
            }
        
        reply = "Sure! Here's a quick comparison of the assessments you asked about:\n"
        for prod in mentioned_products:
            reply += f"\n• {prod['name']}"
            desc = prod.get('description', 'No description available')
            if len(desc) > 150:
                desc = desc[:147] + "..."
            reply += f"\n  {desc}\n"
        
        recs = [
            {"name": p["name"], "url": p["link"], "test_type": get_test_type(p)} 
            for p in mentioned_products
        ]
        
        return {
            "reply": reply,
            "recommendations": recs,
            "end_of_conversation": True
        }


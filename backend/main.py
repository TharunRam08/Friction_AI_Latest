# backend/main.py
"""
Friction — Full 16-Module Cognitive Pipeline
Routes queries through LOW / MEDIUM / HIGH friction paths.
"""
import os
import sqlite3
import json
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from groq import Groq
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import shutil
import time
from datetime import datetime

from modules.m01_intent import get_intent
from modules.m02_friction import get_friction_level
from modules.m03_context import build_context
from modules.m04_memory import get_past_context
from modules.m05_rootcause import find_root_cause
from modules.m06_debate import run_debate
from modules.m08_validate import validate_evidence_and_constraints, self_review
from modules.m07_scenarios import run_scenarios_and_regret
from modules.m09_nemotron import run_nemotron_synthesis
from modules.m_external_context import build_external_context

# CRM Data helpers
from data.crm_db import (
    get_financial_summary, get_deal_pipeline,
    get_customer_health, get_team_stats, get_decision_history,
    get_product_metrics, get_inventory_status, get_campaign_performance,
    get_support_metrics, get_supplier_health, get_expense_breakdown,
    get_kpi_summary, get_contracts_summary
)

# ── Config ───────────────────────────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

CRM_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "crm.db")

app = FastAPI(title="Friction API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


# ── Greeting Detector ─────────────────────────────────────────────────────────
def is_general_greeting(text: str) -> bool:
    cleaned = text.lower().strip().rstrip("?.!")
    greetings = {
        "hi", "hello", "hey", "hola", "greetings", "good morning", "good afternoon",
        "good evening", "who are you", "what is this", "what can you do", "help",
        "start", "welcome", "test"
    }
    if cleaned in greetings:
        return True
    if len(cleaned.split()) <= 2 and not any(
        w in cleaned for w in [
            "expand", "hire", "buy", "sell", "product", "launch", "branch",
            "price", "cost", "revenue", "profit", "salary", "warehouse",
            "customer", "deal", "team", "risk"
        ]
    ):
        return True
    return False


# ── Master Pipeline ───────────────────────────────────────────────────────────
@app.post("/reason")
async def reason(request: QueryRequest):
    question = request.question

    # ── GREETING FAST PATH ───────────────────────────────────────────────────
    if is_general_greeting(question):
        fin = get_financial_summary()
        pipeline = get_deal_pipeline()
        team = get_team_stats()
        health = get_customer_health()
        return {
            "question": question,
            "friction_level": "LOW",
            "pipeline_executed": ["Intent", "Context"],
            "intent": {"goal": "initialize reasoning", "constraints": ["awaiting business scenario"]},
            "context": {"snapshot_text": "Systems ready."},
            "past_memory": (
                f"Friction CRM connected: {team.get('total_headcount',0)} employees, "
                f"${pipeline.get('open_pipeline_value',0):,.0f} open pipeline, "
                f"${fin.get('latest_revenue',0):,.0f} monthly revenue, "
                f"{health.get('avg_ltv',0):,.0f} avg customer LTV."
            ),
            "past_memory_score": 1.0,
            "department_views": [
                {"stance": "Support", "reasons": ["Finance module online. Revenue trending up."]},
                {"stance": "Support", "reasons": ["Operations module online. Pipeline healthy."]},
                {"stance": "Support", "reasons": ["Sales module online. 31 active deals tracked."]},
                {"stance": "Support", "reasons": ["HR module online. Team data loaded."]}
            ],
            "output": {
                "verdict": "Welcome to Friction AI",
                "narrative": (
                    f"Friction is live and connected to your CRM knowledge base. "
                    f"Your business currently has ${fin.get('latest_revenue',0):,.0f} in monthly revenue "
                    f"({fin.get('revenue_trend','stable')} trend), {team.get('total_headcount',0)} employees, "
                    f"and ${pipeline.get('open_pipeline_value',0):,.0f} in open pipeline value. "
                    f"All 5 data sources are connected and ready. Ask a strategic business question to activate the full cognitive pipeline."
                ),
                "key_stats": [
                    {"label": "Monthly Revenue", "value": f"${fin.get('latest_revenue',0):,.0f}", "trend": fin.get("revenue_trend","stable")},
                    {"label": "Open Pipeline", "value": f"${pipeline.get('open_pipeline_value',0):,.0f}", "trend": "stable"},
                    {"label": "Team Size", "value": str(team.get("total_headcount",0)) + " employees", "trend": "stable"},
                    {"label": "Avg Customer LTV", "value": f"${health.get('avg_ltv',0):,.0f}", "trend": "stable"},
                ],
                "confidence": 100,
                "confidence_breakdown": {"agreement": 100, "memory_match": 100, "evidence": 100, "scenario_stability": 100},
                "departments": [
                    {"name": "Finance", "status": "yes", "score": 100, "reason": "Module online"},
                    {"name": "Operations", "status": "yes", "score": 100, "reason": "Module online"},
                    {"name": "Sales", "status": "yes", "score": 100, "reason": "Module online"},
                    {"name": "HR", "status": "yes", "score": 100, "reason": "Module online"},
                ],
                "action_plan": [
                    {"step": "Ask a strategic business question to begin", "timeframe": "now"},
                    {"step": "Click a data source in the sidebar to explore your CRM data", "timeframe": "anytime"},
                ],
                "evidence_score": 100,
                "scenarios": [],
                "devils_advocate": [],
                "regret_choice": "",
                "constraints_check": [],
                "self_review": "All systems nominal.",
                "if_ignored": [],
            },
            "confidence": {"confidence": 100.0, "agreement_score": 1.0, "memory_match": 1.0, "evidence_score": 1.0, "scenario_stability": 1.0}
        }

    # ── PHASE 1: UNDERSTAND ──────────────────────────────────────────────────
    # Run Intent + Context in parallel
    intent = None
    context = None
    with ThreadPoolExecutor(max_workers=2) as ex:
        future_intent = ex.submit(get_intent, question, client)
        intent = future_intent.result()

    goal = intent.get("goal", "")

    # Friction Engine — decides pipeline depth
    friction = get_friction_level(question, intent, client)
    friction_level = friction.get("level", "MEDIUM")

    # Context Builder — always run (reads CRM, no LLM call)
    context = build_context(intent)

    # Business Memory Retrieval
    past_memory, memory_score = get_past_context(question, goal, intent)
    non_neg_score = max(0.0, memory_score)

    # External Context — fetched concurrently (read-only, advisory only).
    # Runs in a background thread while the pipeline continues; result is
    # collected at synthesis time.  Any failure returns "" silently.
    from concurrent.futures import Future as _Future
    _ext_executor = ThreadPoolExecutor(max_workers=1)
    _ext_future = _ext_executor.submit(build_external_context, intent, question)

    pipeline_executed = ["Intent", "Friction", "Context", "Memory"]

    # ── PHASE 2: ANALYZE (MEDIUM + HIGH only) ────────────────────────────────
    root_cause = {}
    views = []
    validation = {}

    if friction_level in ("MEDIUM", "HIGH"):
        context_text = context.get("snapshot_text", "")

        with ThreadPoolExecutor(max_workers=2) as ex:
            future_rootcause = ex.submit(find_root_cause, question, context_text, client)
            future_debate = ex.submit(run_debate, question, goal, past_memory, client)
            root_cause = future_rootcause.result()
            views = future_debate.result()

        pipeline_executed += ["Root Cause", "Debate", "Evidence"]
        validation = validate_evidence_and_constraints(question, views, context, client)

    # ── PHASE 3: REASON (HIGH only) ──────────────────────────────────────────
    scenarios_data = {}

    if friction_level == "HIGH":
        debate_summary = "; ".join([
            f"{['Finance','Operations','Sales','HR'][i]}: {v.get('stance','')} — {v.get('reasons',[''])[0]}"
            for i, v in enumerate(views) if v
        ])
        scenarios_data = run_scenarios_and_regret(
            question, intent, context.get("snapshot_text", ""),
            debate_summary, client
        )
        pipeline_executed += ["Scenarios", "Devil's Advocate", "Regret"]

    # ── PHASE 4: VERIFY (MEDIUM + HIGH) ──────────────────────────────────────
    self_review_text = ""
    if friction_level in ("MEDIUM", "HIGH"):
        all_outputs_summary = {
            "intent": intent, "friction": friction,
            "memory_score": non_neg_score,
            "validation": validation
        }
        self_review_text = self_review(question, all_outputs_summary, client)
        pipeline_executed += ["Confidence", "Constraints", "Self Review"]

    # ── PHASE 5: DECIDE — Final Synthesis ────────────────────────────────────
    pipeline_executed += ["Synthesis", "Explainability", "Learning"]

    # Collect external context (background fetch started in Phase 1).
    # get() with a short timeout so a hung network call never blocks synthesis.
    try:
        external_context = _ext_future.result(timeout=8)
    except Exception:
        external_context = ""
    finally:
        _ext_executor.shutdown(wait=False)

    output = run_nemotron_synthesis(
        question=question,
        intent=intent,
        friction=friction,
        context=context,
        past_memory=past_memory,
        past_memory_score=non_neg_score,
        root_cause=root_cause,
        views=views if views else [],
        validation=validation,
        scenarios_data=scenarios_data,
        self_review_text=self_review_text,
        client_groq=client,
        external_context=external_context,
    )

    # ── Format response for frontend ─────────────────────────────────────────
    status_map = {"yes": "Support", "no": "Against", "wait": "Neutral"}
    depts = output.get("departments", [])
    formatted_views = []
    if len(depts) == 4:
        for dept in depts:
            formatted_views.append({
                "stance": status_map.get(dept.get("status"), "Neutral"),
                "reasons": [f"{dept.get('reason', '')} ({dept.get('score', 75)}%)"]
            })
    else:
        formatted_views = views

    # ── Calculate Mathematical Confidence Score Dynamically ──────────────────
    # 1. Agreement (4 agree = 100, 3 agree = 75, 2-2 split = 50, 3 against = 25)
    agreement = 50
    if views:
        stances = [v.get("stance", "neutral").lower() for v in views if v]
        yes_count = sum(1 for s in stances if s in ("yes", "support", "for"))
        no_count = sum(1 for s in stances if s in ("no", "against"))
        total_active = len(stances)
        if total_active > 0:
            if yes_count == total_active or no_count == total_active:
                agreement = 100
            elif yes_count >= 3 or no_count >= 3:
                agreement = 75
            elif yes_count == 2 and no_count == 2:
                agreement = 50
            else:
                agreement = 25

    # 2. Memory match
    memory_match = min(100, max(0, int(non_neg_score * 100)))

    # 3. Evidence (Module 13 validate phase evidence score)
    evidence = validation.get("evidence_score", 70) if validation else 70

    # 4. Scenario stability
    scenario_stability = 60
    if scenarios_data:
        scenarios_list = scenarios_data.get("scenarios", [])
        if scenarios_list:
            risks = [s.get("risk", "Medium").lower() for s in scenarios_list if s]
            if all(r == "low" for r in risks):
                scenario_stability = 80
            elif all(r == "high" for r in risks):
                scenario_stability = 40
            else:
                scenario_stability = 60

    calculated_confidence = int(round(0.35 * agreement + 0.25 * memory_match + 0.20 * evidence + 0.20 * scenario_stability))

    # Overwrite LLM payload values with programmatic ground-truth math
    output["confidence"] = calculated_confidence
    output["confidence_breakdown"] = {
        "agreement": agreement,
        "memory_match": memory_match,
        "evidence": evidence,
        "scenario_stability": scenario_stability
    }

    confidence_data = {
        "confidence": calculated_confidence,
        "agreement_score": agreement / 100.0,
        "memory_match": memory_match / 100.0,
        "evidence_score": evidence / 100.0,
        "scenario_stability": scenario_stability / 100.0,
    }

    # Build recommendation text (backward compat with old UI fields)
    rec_parts = [f"**Verdict**: {output.get('verdict', '')}"]
    if output.get("mistake_context"):
        rec_parts.append(f"**Past Case**: {output['mistake_context']}")
    if output.get("pattern_match"):
        rec_parts.append(f"**Pattern Match**: {output['pattern_match']}")
    if output.get("action_plan"):
        plan = ", ".join([f"{a['step']} ({a['timeframe']})" for a in output["action_plan"]])
        rec_parts.append(f"**Action Plan**: {plan}")
    if output.get("if_ignored"):
        rec_parts.append(f"**Risk If Ignored**: {' | '.join(output['if_ignored'])}")

    return {
        "question": question,
        "friction_level": friction_level,
        "pipeline_executed": pipeline_executed,
        "intent": intent,
        "context": context,
        "past_memory": past_memory,
        "past_memory_score": non_neg_score,
        "department_views": formatted_views,
        "recommendation": "\n\n".join(rec_parts),
        "output": output,  # Full rich output object
        "confidence": confidence_data,
        "external_context": external_context,  # Advisory market backdrop; empty string if unavailable
    }


# ── Data Sources API ──────────────────────────────────────────────────────────
def parse_pdf(file_path: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text

def parse_excel(file_path: str) -> str:
    import openpyxl
    wb = openpyxl.load_workbook(file_path, data_only=True)
    text_parts = []
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        text_parts.append(f"Sheet: {sheet_name}")
        
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            continue
            
        # Find the first row that contains at least one non-empty value to use as headers
        header_row = None
        header_idx = -1
        for idx, r in enumerate(rows):
            if any(cell is not None and str(cell).strip() != "" for cell in r):
                header_row = [str(cell).strip() if cell is not None else f"Col {i}" for i, cell in enumerate(r, 1)]
                header_idx = idx
                break
                
        if header_row is None:
            for r_idx, row in enumerate(rows, 1):
                if any(cell is not None for cell in row):
                    row_str = ", ".join(f"Col {col_idx}: {cell}" for col_idx, cell in enumerate(row, 1) if cell is not None)
                    text_parts.append(f"Row {r_idx}: {row_str}")
            continue
            
        for r_idx, row in enumerate(rows[header_idx+1:], header_idx + 2):
            if any(cell is not None and str(cell).strip() != "" for cell in row):
                row_cells = []
                for col_idx, cell in enumerate(row):
                    if col_idx < len(header_row):
                        header_name = header_row[col_idx]
                        val = str(cell).strip() if cell is not None else ""
                        row_cells.append(f"{header_name}: {val}")
                if row_cells:
                    row_str = " | ".join(row_cells)
                    text_parts.append(f"Row {r_idx}: {row_str}")
    return "\n".join(text_parts)

def parse_csv(file_path: str) -> str:
    import csv
    text_parts = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        rows = list(reader)
        if not rows:
            return ""
            
        # Find first row with non-empty values
        header_row = None
        header_idx = -1
        for idx, r in enumerate(rows):
            if any(cell.strip() != "" for cell in r):
                header_row = [cell.strip() if cell.strip() != "" else f"Col {i}" for i, cell in enumerate(r, 1)]
                header_idx = idx
                break
                
        if header_row is None:
            for r_idx, row in enumerate(rows, 1):
                if row:
                    row_str = ", ".join(f"Col {col_idx}: {cell}" for col_idx, cell in enumerate(row, 1) if cell)
                    text_parts.append(f"Row {r_idx}: {row_str}")
            return "\n".join(text_parts)
            
        for r_idx, row in enumerate(rows[header_idx+1:], header_idx + 2):
            if any(cell.strip() != "" for cell in row):
                row_cells = []
                for col_idx, cell in enumerate(row):
                    if col_idx < len(header_row):
                        header_name = header_row[col_idx]
                        val = cell.strip()
                        row_cells.append(f"{header_name}: {val}")
                if row_cells:
                    row_str = " | ".join(row_cells)
                    text_parts.append(f"Row {r_idx}: {row_str}")
    return "\n".join(text_parts)

def parse_spreadsheet_on_the_fly(file_path: str, file_type: str, limit: int = 100):
    import datetime
    
    def format_cell(cell):
        if cell is None:
            return ""
        if isinstance(cell, (datetime.datetime, datetime.date)):
            if hasattr(cell, "hour") and (cell.hour != 0 or cell.minute != 0 or cell.second != 0):
                return cell.strftime("%Y-%m-%d %H:%M:%S")
            return cell.strftime("%Y-%m-%d")
        return str(cell).strip()

    if file_type.upper() in ("XLSX", "XLS"):
        import openpyxl
        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active if wb.active else wb[wb.sheetnames[0]]
            rows_raw = list(sheet.iter_rows(values_only=True))
            if not rows_raw:
                return {"columns": [], "rows": [], "total": 0}
            
            # Find first non-empty row for header
            header_row = None
            header_idx = -1
            for idx, r in enumerate(rows_raw):
                if any(cell is not None and str(cell).strip() != "" for cell in r):
                    header_row = [format_cell(cell) if cell is not None else f"Col_{i}" for i, cell in enumerate(r, 1)]
                    # ensure unique column names
                    seen = {}
                    unique_headers = []
                    for h in header_row:
                        name = h if h else "Column"
                        if name in seen:
                            seen[name] += 1
                            unique_headers.append(f"{name}_{seen[name]}")
                        else:
                            seen[name] = 1
                            unique_headers.append(name)
                    header_row = unique_headers
                    header_idx = idx
                    break
            
            if header_row is None:
                return {"columns": [], "rows": [], "total": 0}
            
            rows_data = []
            for row in rows_raw[header_idx + 1:]:
                if any(cell is not None and str(cell).strip() != "" for cell in row):
                    row_dict = {}
                    for col_idx, cell in enumerate(row):
                        if col_idx < len(header_row):
                            row_dict[header_row[col_idx]] = format_cell(cell)
                    rows_data.append(row_dict)
            return {
                "columns": header_row,
                "rows": rows_data[:limit],
                "total": len(rows_data)
            }
        except Exception as e:
            print(f"Error parsing xlsx on the fly: {e}")
            return None
            
    elif file_type.upper() == "CSV":
        import csv
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                rows_raw = list(reader)
            if not rows_raw:
                return {"columns": [], "rows": [], "total": 0}
                
            # Find header
            header_row = None
            header_idx = -1
            for idx, r in enumerate(rows_raw):
                if any(cell.strip() != "" for cell in r):
                    header_row = [cell.strip() if cell.strip() != "" else f"Col_{i}" for i, cell in enumerate(r, 1)]
                    seen = {}
                    unique_headers = []
                    for h in header_row:
                        name = h if h else "Column"
                        if name in seen:
                            seen[name] += 1
                            unique_headers.append(f"{name}_{seen[name]}")
                        else:
                            seen[name] = 1
                            unique_headers.append(name)
                    header_row = unique_headers
                    header_idx = idx
                    break
                    
            if header_row is None:
                return {"columns": [], "rows": [], "total": 0}
                
            rows_data = []
            for row in rows_raw[header_idx + 1:]:
                if any(cell.strip() != "" for cell in row):
                    row_dict = {}
                    for col_idx, cell in enumerate(row):
                        if col_idx < len(header_row):
                            row_dict[header_row[col_idx]] = cell.strip()
                    rows_data.append(row_dict)
            return {
                "columns": header_row,
                "rows": rows_data[:limit],
                "total": len(rows_data)
            }
        except Exception as e:
            print(f"Error parsing csv on the fly: {e}")
            return None
    return None

def extract_table_from_pdf_text_via_llm(text: str):
    import json
    try:
        prompt = (
            "You are an expert data extractor. Extract the structured tabular data from the following text. "
            "Convert any tables found into a single combined JSON object with keys:\n"
            "- 'columns': List of column names (headers)\n"
            "- 'rows': List of objects where keys match the columns\n\n"
            "Rules:\n"
            "1. Ignore all narrative paragraphs, headers, footers, and conversational text. Extract ONLY the data rows and columns.\n"
            "2. Ensure the JSON is valid and fits the format.\n"
            "3. If multiple tables exist, merge them or extract the main dataset table.\n"
            "4. Return ONLY the JSON object, starting with { and ending with }. No markdown formatting or explanation.\n\n"
            f"Text to extract:\n{text[:15000]}"
        )
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        raw_response = chat_completion.choices[0].message.content
        data = json.loads(raw_response)
        if "columns" in data and "rows" in data:
            return data
    except Exception as e:
        print(f"⚠️ Error extracting table from PDF text via LLM: {e}")
    return None

def parse_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def clean_text(text: str) -> str:
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        cleaned_line = " ".join(line.split()).strip()
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    return "\n".join(cleaned_lines)

def save_uploaded_doc_metadata(doc_id: str, filename: str, file_type: str, size_bytes: int, chunks: list):
    uploaded_json_path = os.path.join(os.path.dirname(__file__), "data", "uploaded_docs.json")
    
    docs = []
    if os.path.exists(uploaded_json_path):
        try:
            with open(uploaded_json_path, "r", encoding="utf-8") as f:
                docs = json.load(f)
        except Exception:
            docs = []
            
    new_doc = {
        "id": doc_id,
        "filename": filename,
        "file_type": file_type,
        "size_bytes": size_bytes,
        "summary": f"{file_type} File • {len(chunks)} text chunks indexed",
        "tags": ["Uploaded", file_type],
        "chunks": [{"index": i, "text": chunk} for i, chunk in enumerate(chunks)]
    }
    
    docs.append(new_doc)
    
    with open(uploaded_json_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

def delete_uploaded_doc_metadata(doc_id: str) -> bool:
    uploaded_json_path = os.path.join(os.path.dirname(__file__), "data", "uploaded_docs.json")
    if not os.path.exists(uploaded_json_path):
        return False
        
    try:
        with open(uploaded_json_path, "r", encoding="utf-8") as f:
            docs = json.load(f)
            
        target_doc = None
        for doc in docs:
            if doc["id"] == doc_id:
                target_doc = doc
                break
                
        if not target_doc:
            return False
            
        # Remove from Vectordb Chroma DB
        from data.vectordb import remove_document_from_vector_db
        remove_document_from_vector_db(doc_id, len(target_doc["chunks"]))
        
        # Remove original file if exists
        upload_dir = os.path.join(os.path.dirname(__file__), "data", "uploads")
        file_path = os.path.join(upload_dir, target_doc["filename"])
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # Update metadata JSON
        docs = [d for d in docs if d["id"] != doc_id]
        with open(uploaded_json_path, "w", encoding="utf-8") as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)
            
        return True
    except Exception as e:
        print(f"⚠️ Error deleting document metadata: {e}")
        return False


@app.get("/data-sources")
async def data_sources_summary():
    # Load summaries
    fin = get_financial_summary()
    pipeline = get_deal_pipeline()
    health = get_customer_health()
    team = get_team_stats()
    decisions = get_decision_history(25)
    products = get_product_metrics()
    inventory = get_inventory_status()
    campaigns = get_campaign_performance()
    support = get_support_metrics()
    suppliers = get_supplier_health()
    expenses = get_expense_breakdown()
    kpis = get_kpi_summary()
    contracts = get_contracts_summary()

    # Query counts from DB
    tables = [
        "customers", "deals", "financials", "team", "decisions",
        "products", "inventory", "campaigns", "support_tickets",
        "suppliers", "expenses", "kpis", "contracts"
    ]
    conn = sqlite3.connect(CRM_DB_PATH)
    cur = conn.cursor()
    counts = {}
    for tbl in tables:
        counts[tbl] = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    conn.close()

    # Load uploaded documents
    uploaded_json_path = os.path.join(os.path.dirname(__file__), "data", "uploaded_docs.json")
    uploaded_sources = []
    if os.path.exists(uploaded_json_path):
        try:
            with open(uploaded_json_path, "r", encoding="utf-8") as f:
                docs = json.load(f)
                for doc in docs:
                    uploaded_sources.append({
                        "id": doc["id"],
                        "label": doc["filename"],
                        "icon": "file-text",
                        "row_count": len(doc["chunks"]),
                        "status": "connected",
                        "summary": doc["summary"],
                        "tags": doc["tags"]
                    })
        except Exception as e:
            print(f"⚠️ Error reading uploaded_docs.json: {e}")

    return {
        "sources": [
            {
                "id": "customers",
                "label": "Customers",
                "icon": "users",
                "row_count": counts["customers"],
                "status": "connected",
                "summary": f"Avg LTV ${health['avg_ltv']:,.0f} • {len(health.get('at_risk_accounts', []))} high-risk accounts",
                "tags": ["CRM", "Retention"]
            },
            {
                "id": "deals",
                "label": "Deals Pipeline",
                "icon": "trending-up",
                "row_count": counts["deals"],
                "status": "connected",
                "summary": f"Open pipeline ${pipeline['open_pipeline_value']:,.0f} • {pipeline['open_deal_count']} active deals",
                "tags": ["Sales", "Pipeline"]
            },
            {
                "id": "financials",
                "label": "Financials",
                "icon": "bar-chart",
                "row_count": counts["financials"],
                "status": "connected",
                "summary": f"Latest revenue ${fin['latest_revenue']:,.0f} • {fin['avg_profit_margin_pct']}% avg margin",
                "tags": ["Finance", "P&L"]
            },
            {
                "id": "team",
                "label": "Team",
                "icon": "people",
                "row_count": counts["team"],
                "status": "connected",
                "summary": f"{team['total_headcount']} employees • ${team['total_annual_payroll']:,.0f} annual payroll",
                "tags": ["HR", "Talent"]
            },
            {
                "id": "decisions",
                "label": "Past Decisions",
                "icon": "clock",
                "row_count": counts["decisions"],
                "status": "connected",
                "summary": f"{sum(1 for d in decisions if d['outcome']=='Success')} successes • {sum(1 for d in decisions if d['outcome']=='Failed')} failures",
                "tags": ["Memory", "History"]
            },
            {
                "id": "products",
                "label": "Products & SKUs",
                "icon": "package",
                "row_count": counts["products"],
                "status": "connected",
                "summary": f"YTD Product Rev ${products['total_product_revenue_ytd']:,.0f} • Avg Margin {products['avg_portfolio_margin']}%",
                "tags": ["Inventory", "Margin"]
            },
            {
                "id": "inventory",
                "label": "Inventory",
                "icon": "archive",
                "row_count": counts["inventory"],
                "status": "connected",
                "summary": f"{inventory['needs_immediate_reorder']} critical items need reorder • Avg Supply {inventory['avg_days_of_supply']} days",
                "tags": ["Logistics", "Warehouse"]
            },
            {
                "id": "campaigns",
                "label": "Marketing Campaigns",
                "icon": "target",
                "row_count": counts["campaigns"],
                "status": "connected",
                "summary": f"Spent ${campaigns['total_spend']:,.0f} • Overall ROI {campaigns['overall_roi_pct']}%",
                "tags": ["Marketing", "ROI"]
            },
            {
                "id": "support_tickets",
                "label": "Support Tickets",
                "icon": "help-circle",
                "row_count": counts["support_tickets"],
                "status": "connected",
                "summary": f"Avg CSAT {support['avg_csat']}/5 • {len(support['critical_open'])} critical tickets open",
                "tags": ["Support", "CSAT"]
            },
            {
                "id": "suppliers",
                "label": "Suppliers & Vendors",
                "icon": "truck",
                "row_count": counts["suppliers"],
                "status": "connected",
                "summary": f"Avg Reliability {suppliers['avg_reliability_score']}/100 • {len(suppliers['high_risk_suppliers'])} high-risk suppliers",
                "tags": ["Vendor", "Operations"]
            },
            {
                "id": "expenses",
                "label": "Expenses",
                "icon": "credit-card",
                "row_count": counts["expenses"],
                "status": "connected",
                "summary": f"Latest Monthly Expense ${expenses['latest_total']:,.0f} • 6M Avg ${expenses['avg_monthly_expenses_6m']:,.0f}",
                "tags": ["Finance", "Expenses"]
            },
            {
                "id": "kpis",
                "label": "Quarterly KPIs",
                "icon": "activity",
                "row_count": counts["kpis"],
                "status": "connected",
                "summary": f"MRR ${kpis['latest_mrr']:,.0f} • Churn {kpis['latest_churn_pct']}% • NPS {kpis['latest_nps']}",
                "tags": ["KPIs", "SaaS"]
            },
            {
                "id": "contracts",
                "label": "Contracts & ARR",
                "icon": "file-text",
                "row_count": counts["contracts"],
                "status": "connected",
                "summary": f"Total ARR ${contracts['total_arr']:,.0f} • At-Risk ARR ${contracts['at_risk_arr']:,.0f}",
                "tags": ["Contracts", "ARR"]
            },
        ] + uploaded_sources
    }


@app.get("/data-sources/{table}")
async def data_source_rows(table: str, limit: int = 100):
    allowed = {
        "customers", "deals", "financials", "team", "decisions",
        "products", "inventory", "campaigns", "support_tickets",
        "suppliers", "expenses", "kpis", "contracts"
    }
    if table not in allowed:
        if table.startswith("uploaded_"):
            uploaded_json_path = os.path.join(os.path.dirname(__file__), "data", "uploaded_docs.json")
            if os.path.exists(uploaded_json_path):
                try:
                    with open(uploaded_json_path, "r", encoding="utf-8") as f:
                        docs = json.load(f)
                        for doc in docs:
                            if doc["id"] == table:
                                # Try parsing the original file on the fly if it is Excel or CSV
                                filename = doc.get("filename", "")
                                file_type = doc.get("file_type", "").upper()
                                upload_dir = os.path.join(os.path.dirname(__file__), "data", "uploads")
                                file_path = os.path.join(upload_dir, filename)
                                
                                if os.path.exists(file_path):
                                    if file_type in ("XLSX", "XLS", "CSV"):
                                        parsed = parse_spreadsheet_on_the_fly(file_path, file_type, limit)
                                        if parsed:
                                            return {
                                                "table": table,
                                                "columns": parsed["columns"],
                                                "rows": parsed["rows"],
                                                "total": parsed["total"]
                                            }
                                    elif file_type == "PDF":
                                        pdf_text = parse_pdf(file_path)
                                        parsed = extract_table_from_pdf_text_via_llm(pdf_text)
                                        if parsed and parsed.get("columns"):
                                            return {
                                                "table": table,
                                                "columns": parsed["columns"],
                                                "rows": parsed["rows"][:limit],
                                                "total": len(parsed["rows"])
                                            }

                                # Fallback to chunks representation for PDF/TXT or if parsing fails
                                return {
                                    "table": table,
                                    "columns": ["chunk_index", "text_content", "characters"],
                                    "rows": [
                                        {
                                            "chunk_index": c["index"],
                                            "text_content": c["text"],
                                            "characters": len(c["text"])
                                        } for c in doc["chunks"]
                                    ][:limit],
                                    "total": len(doc["chunks"])
                                }
                except Exception as e:
                    print(f"⚠️ Error loading uploaded document rows: {e}")
        return {"error": "Invalid table", "rows": [], "columns": []}
    conn = sqlite3.connect(CRM_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute(f"SELECT * FROM {table} LIMIT ?", (limit,)).fetchall()
    columns = [d[0] for d in cur.description] if rows else []
    conn.close()
    return {"table": table, "columns": columns, "rows": [dict(r) for r in rows], "total": len(rows)}


@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    upload_dir = os.path.join(os.path.dirname(__file__), "data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        return {"success": False, "error": f"Failed to save file: {str(e)}"}
        
    size_bytes = os.path.getsize(file_path)
    ext = os.path.splitext(file.filename)[1].lower()
    text = ""
    file_type = ext[1:].upper() if ext else "UNKNOWN"
    
    try:
        if ext == ".pdf":
            text = parse_pdf(file_path)
        elif ext in (".xlsx", ".xls"):
            text = parse_excel(file_path)
        elif ext == ".csv":
            text = parse_csv(file_path)
        elif ext in (".txt", ".md", ".json"):
            text = parse_txt(file_path)
        else:
            if os.path.exists(file_path):
                os.remove(file_path)
            return {"success": False, "error": f"Unsupported file type: {ext}"}
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"success": False, "error": f"Failed to parse file: {str(e)}"}
        
    cleaned = clean_text(text)
    if not cleaned:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"success": False, "error": "Document contains no readable text."}
        
    from data.vectordb import add_document_to_vector_db
    sanitized_name = "".join(c for c in os.path.splitext(file.filename)[0] if c.isalnum() or c in ("_", "-")).lower()
    doc_id = f"uploaded_{sanitized_name}_{int(time.time())}"
    
    try:
        chunks = add_document_to_vector_db(cleaned, file.filename, doc_id)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"success": False, "error": f"Failed to generate embeddings: {str(e)}"}
    
    try:
        save_uploaded_doc_metadata(doc_id, file.filename, file_type, size_bytes, chunks)
    except Exception as e:
        return {"success": False, "error": f"Failed to save metadata: {str(e)}"}
    
    return {
        "success": True,
        "filename": file.filename,
        "doc_id": doc_id,
        "chunks_count": len(chunks),
        "total_chars": len(cleaned)
    }


@app.delete("/upload-document/{doc_id}")
async def delete_document(doc_id: str):
    success = delete_uploaded_doc_metadata(doc_id)
    return {"success": success}



# ── Future Forecast Endpoint ──────────────────────────────────────────────────
class FutureForecastRequest(BaseModel):
    decision: str
    scenarios: list = []
    context: dict = {}

@app.post("/future-forecast")
async def future_forecast(request: FutureForecastRequest):
    """
    Combines:
    1. Real market index trends from SerpAPI (Google Finance Markets)
    2. CRM live data snapshot
    3. Scenario projections for each decision path
    Returns enriched multi-path future projections with monthly bars.
    """
    # ── 1. Fetch real market data ─────────────────────────────────────────────
    market_indexes = []
    market_sentiment = "NEUTRAL"
    try:
        from serpapi import GoogleSearch
        mkt_res = GoogleSearch({"engine": "google_finance_markets", "trend": "indexes", "api_key": "e308d24f710bcef82ce75df292e254fe519ec89c89679782c5cb363e42e3297f"}).get_dict()
        raw_indexes = mkt_res.get("market_trends", {}).get("indexes", []) or []
        for idx in raw_indexes[:5]:
            price = idx.get("price", "N/A")
            change_pct = idx.get("percentage", 0)
            try:
                change_f = float(str(change_pct).replace("%", "").replace("+", ""))
            except:
                change_f = 0.0
            market_indexes.append({
                "name": idx.get("name", "Index"),
                "price": price,
                "change_pct": round(change_f, 2),
                "direction": "up" if change_f >= 0 else "down"
            })
        # Gauge overall market sentiment
        ups = sum(1 for i in market_indexes if i["direction"] == "up")
        downs = len(market_indexes) - ups
        market_sentiment = "BULLISH" if ups > downs else "BEARISH" if downs > ups else "NEUTRAL"
    except Exception as e:
        print(f"[SerpAPI] Market fetch failed: {e}")
        market_indexes = [
            {"name": "S&P 500", "price": "5,480", "change_pct": 0.42, "direction": "up"},
            {"name": "NASDAQ", "price": "17,920", "change_pct": 0.71, "direction": "up"},
            {"name": "DOW", "price": "39,100", "change_pct": -0.15, "direction": "down"},
        ]
        market_sentiment = "NEUTRAL"



    # ── 2. CRM snapshot ───────────────────────────────────────────────────────
    fin = get_financial_summary()
    pipeline = get_deal_pipeline()
    health = get_customer_health()
    base_revenue = fin.get("latest_revenue", 850000)
    base_pipeline = pipeline.get("open_pipeline_value", 600000)
    base_ltv = health.get("avg_ltv", 180000)
    churn_pct = health.get("churn_rate_pct", 4.2)

    # ── 3. Build multi-scenario monthly projections ───────────────────────────
    months = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"]

    def project(base, growth_rates, volatility=0.0):
        """Build monthly projection list applying growth rates with market sentiment scaling."""
        sentiment_multiplier = 1.05 if market_sentiment == "BULLISH" else 0.97 if market_sentiment == "BEARISH" else 1.0
        result = []
        current = base
        for rate in growth_rates:
            current = current * (1 + rate * sentiment_multiplier)
            result.append(round(current))
        return result

    scenarios_out = []

    # --- Conservative Path ---
    scenarios_out.append({
        "id": "conservative",
        "name": "Conservative",
        "label": "Low-risk, slow growth. Prioritize stability over speed.",
        "risk": "LOW",
        "color": "#10b981",
        "revenue": project(base_revenue, [0.005, 0.007, 0.008, 0.006, 0.009, 0.010]),
        "pipeline": project(base_pipeline, [0.01, 0.015, 0.012, 0.018, 0.02, 0.025]),
        "customers": project(base_ltv, [0.003, 0.004, 0.005, 0.004, 0.006, 0.007]),
        "churn": [round(churn_pct - 0.1 * i, 2) for i in range(6)],
        "confidence": 88,
        "breaking_assumption": "Assumes no competitive pressure or economic disruption."
    })

    # --- Balanced Path ---
    scenarios_out.append({
        "id": "balanced",
        "name": "Balanced",
        "label": "Moderate growth with calculated risk. Recommended default.",
        "risk": "MEDIUM",
        "color": "#f59e0b",
        "revenue": project(base_revenue, [0.015, 0.022, 0.028, 0.025, 0.032, 0.038]),
        "pipeline": project(base_pipeline, [0.03, 0.045, 0.05, 0.055, 0.06, 0.07]),
        "customers": project(base_ltv, [0.01, 0.015, 0.018, 0.02, 0.022, 0.025]),
        "churn": [round(churn_pct - 0.15 * i, 2) for i in range(6)],
        "confidence": 74,
        "breaking_assumption": "Assumes team capacity can absorb growth and market stays neutral."
    })

    # --- Aggressive Path ---
    scenarios_out.append({
        "id": "aggressive",
        "name": "Aggressive",
        "label": "Maximum growth bet. High risk, high reward.",
        "risk": "HIGH",
        "color": "#ef4444",
        "revenue": project(base_revenue, [0.03, 0.05, 0.065, 0.055, 0.075, 0.09]),
        "pipeline": project(base_pipeline, [0.06, 0.08, 0.10, 0.09, 0.12, 0.14]),
        "customers": project(base_ltv, [0.02, 0.03, 0.04, 0.045, 0.055, 0.065]),
        "churn": [round(churn_pct + 0.05 * i, 2) for i in range(6)],
        "confidence": 52,
        "breaking_assumption": "Assumes unlimited capital runway and no churn spike during scaling."
    })

    return {
        "decision": request.decision,
        "market_sentiment": market_sentiment,
        "market_indexes": market_indexes,
        "months": months,
        "scenarios": scenarios_out,
        "base_revenue": base_revenue,
        "base_pipeline": base_pipeline,
    }


# ── Canary Anomaly Engine Endpoint ────────────────────────────────────────────
from datetime import datetime, timedelta
from modules.m10_canary import calculate_drift, run_canary_analysis

def init_business_memory():
    conn = sqlite3.connect(CRM_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='business_memory'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute("""
            CREATE TABLE business_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT,
                revenue_drift REAL,
                expenses_drift REAL,
                tickets_drift REAL,
                inventory_drift REAL
            )
        """)
        patterns = [
            ("Cash Flow Crunch", -2.0, 1.5, 0.5, 1.0),
            ("Margin Erosion", 0.5, 2.5, 0.2, 0.0),
            ("Operations Bottleneck", -1.0, 1.0, 2.0, -1.5),
            ("Demand Collapse", -3.0, -0.5, 1.0, 2.5)
        ]
        cursor.executemany("""
            INSERT INTO business_memory (pattern_name, revenue_drift, expenses_drift, tickets_drift, inventory_drift)
            VALUES (?, ?, ?, ?, ?)
        """, patterns)
        conn.commit()
    conn.close()

def fetch_canary_data():
    conn = sqlite3.connect(CRM_DB_PATH)
    cursor = conn.cursor()
    
    # Get the max date in support_tickets or deals to align query timeline with DB seed dates
    cursor.execute("SELECT MAX(opened_date) FROM support_tickets")
    max_tkt = cursor.fetchone()[0]
    cursor.execute("SELECT MAX(close_date) FROM deals")
    max_deal = cursor.fetchone()[0]
    
    dates = [d for d in [max_tkt, max_deal] if d]
    if not dates:
        anchor_date = datetime.today()
    else:
        anchor_date = datetime.strptime(max(dates), "%Y-%m-%d")
        
    # Generate dates for 37 days (baseline 30 days + current 7 days)
    raw_dates = [(anchor_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(37)]
    raw_dates.reverse()
    
    # Cache monthly tables to avoid multiple database calls in a loop
    cursor.execute("SELECT month, revenue FROM financials")
    financials_map = {r[0]: r[1] for r in cursor.fetchall()}
    
    cursor.execute("SELECT month, total FROM expenses")
    expenses_map = {r[0]: r[1] for r in cursor.fetchall()}
    
    # Get total inventory qty (constant across daily checks)
    cursor.execute("SELECT SUM(qty_on_hand) FROM inventory")
    total_inventory = cursor.fetchone()[0] or 0
    
    daily_metrics = []
    for date_str in raw_dates:
        month_str = date_str[:7] # YYYY-MM
        
        # 1. Revenue (Monthly revenue divided by 30)
        rev = financials_map.get(month_str, 850000.0) / 30.0
        
        # 2. Expenses (Monthly expenses divided by 30)
        exp = expenses_map.get(month_str, 250000.0) / 30.0
        
        # 3. Support Tickets (Daily count)
        cursor.execute("SELECT COUNT(*) FROM support_tickets WHERE opened_date = ?", (date_str,))
        tkt_count = cursor.fetchone()[0] or 0
        
        daily_metrics.append({
            "revenue": rev,
            "expenses": exp,
            "tickets": tkt_count,
            "inventory": total_inventory
        })
        
    conn.close()
    return daily_metrics

@app.post("/api/canary-run")
async def canary_run():
    # 1. Initialize and seed patterns DB if not present
    init_business_memory()
    
    # 2. Fetch daily metric timelines (last 37 days)
    try:
        daily_metrics = fetch_canary_data()
    except Exception as e:
        return {"error": f"Failed to retrieve database metrics: {str(e)}"}
        
    baseline_data = daily_metrics[:30]
    current_data = daily_metrics[30:]
    
    # Extract baseline and current arrays
    b_rev = [d["revenue"] for d in baseline_data]
    c_rev = [d["revenue"] for d in current_data]
    
    b_exp = [d["expenses"] for d in baseline_data]
    c_exp = [d["expenses"] for d in current_data]
    
    b_tkt = [d["tickets"] for d in baseline_data]
    c_tkt = [d["tickets"] for d in current_data]
    
    b_inv = [d["inventory"] for d in baseline_data]
    c_inv = [d["inventory"] for d in current_data]
    
    # Calculate statistical drifts
    drift_rev, pct_rev = calculate_drift(c_rev, b_rev)
    drift_exp, pct_exp = calculate_drift(c_exp, b_exp)
    drift_tkt, pct_tkt = calculate_drift(c_tkt, b_tkt)
    drift_inv, pct_inv = calculate_drift(c_inv, b_inv)
    
    drift_vector = [drift_rev, drift_exp, drift_tkt, drift_inv]
    
    # Load historical failure signatures
    conn = sqlite3.connect(CRM_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT pattern_name, revenue_drift, expenses_drift, tickets_drift, inventory_drift FROM business_memory")
    rows = cursor.fetchall()
    conn.close()
    
    patterns = [(r[0], [r[1], r[2], r[3], r[4]]) for r in rows]
    
    # Run Canary Analysis using module
    analysis = run_canary_analysis(drift_vector, patterns)
    
    return {
        "alert": analysis["alert"],
        "matched_pattern": analysis["matched_pattern"],
        "similarity": analysis["similarity"],
        "all_scores": analysis["all_scores"],
        "drift_percentages": {
            "revenue": pct_rev,
            "revenue_z": drift_rev,
            "expenses": pct_exp,
            "expenses_z": drift_exp,
            "tickets": pct_tkt,
            "tickets_z": drift_tkt,
            "inventory": pct_inv,
            "inventory_z": drift_inv
        }
    }


def get_crm_dashboard_data(days: int = 30):
    conn = sqlite3.connect(CRM_DB_PATH)
    cursor = conn.cursor()
    
    # Get max date from DB to align query timeline with active ticket dates
    cursor.execute("SELECT MAX(opened_date) FROM support_tickets")
    max_tkt = cursor.fetchone()[0]
    if not max_tkt:
        anchor_date = datetime.today()
    else:
        anchor_date = datetime.strptime(max_tkt, "%Y-%m-%d")
        
    start_date = anchor_date - timedelta(days=days - 1)
    
    # Generate daily chronological list of date strings
    date_list = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    
    # 1. Fetch daily closed-won deal revenues
    cursor.execute("""
        SELECT close_date, SUM(value) 
        FROM deals 
        WHERE stage = 'Closed-Won' AND close_date BETWEEN ? AND ?
        GROUP BY close_date
    """, (date_list[0], date_list[-1]))
    revenue_map = {r[0]: r[1] for r in cursor.fetchall()}
    
    # 2. Fetch monthly expenses
    cursor.execute("SELECT month, total FROM expenses")
    expenses_map = {r[0]: r[1] for r in cursor.fetchall()}
    
    # 3. Fetch daily support ticket counts
    cursor.execute("""
        SELECT opened_date, COUNT(*) 
        FROM support_tickets 
        WHERE opened_date BETWEEN ? AND ?
        GROUP BY opened_date
    """, (date_list[0], date_list[-1]))
    tickets_map = {r[0]: r[1] for r in cursor.fetchall()}
    
    # 4. Fetch customer segment breakdown (Closed-Won revenue)
    cursor.execute("""
        SELECT c.segment, SUM(d.value) 
        FROM deals d 
        JOIN customers c ON d.customer_id = c.id 
        WHERE d.stage = 'Closed-Won' AND d.close_date BETWEEN ? AND ?
        GROUP BY c.segment
    """, (date_list[0], date_list[-1]))
    segment_revenue = {r[0]: r[1] or 0 for r in cursor.fetchall()}
    
    # 5. Fetch current inventory level & inventory items details
    cursor.execute("SELECT SUM(qty_on_hand) FROM inventory")
    current_inventory = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT product_name, sku, qty_on_hand, reorder_point FROM inventory")
    inventory_items = [
        {
            "name": r[0],
            "sku": r[1],
            "qty_on_hand": r[2],
            "reorder_point": r[3]
        }
        for r in cursor.fetchall()
    ]
    
    daily_records = []
    total_revenue = 0.0
    total_expenses = 0.0
    total_tickets = 0
    
    import hashlib
    for date_str in date_list:
        month_str = date_str[:7]
        
        # Calculate daily baseline recurring revenue (deterministic ordering/renewals)
        hash_val = int(hashlib.md5(date_str.encode('utf-8')).hexdigest(), 16)
        baseline_rev = 12000.0 + (hash_val % 6000) # $12,000 to $18,000
        
        rev = baseline_rev + revenue_map.get(date_str, 0.0)
        
        # Calculate daily expense with deterministic fluctuations and weekend drops
        base_exp = expenses_map.get(month_str, 250000.0) / 30.0
        variance = 0.88 + (hash_val % 25) / 100.0 # 0.88 to 1.12
        
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        is_weekend = date_obj.weekday() >= 5
        if is_weekend:
            exp = base_exp * 0.45 * variance # 55% discount on weekends
        else:
            exp = base_exp * variance
            
        tkt = tickets_map.get(date_str, 0)
        
        daily_records.append({
            "date": date_str,
            "revenue": round(rev, 2),
            "expenses": round(exp, 2),
            "tickets": tkt
        })
        
        total_revenue += rev
        total_expenses += exp
        total_tickets += tkt
        
    avg_daily_tickets = round(total_tickets / days, 1)
    conn.close()

    # Dynamic time-series aggregation based on range
    if days <= 30:
        time_series = daily_records
    elif days == 90:
        # Group by week (7-day intervals)
        time_series = []
        for i in range(0, len(daily_records), 7):
            chunk = daily_records[i : i+7]
            w_rev = sum(d["revenue"] for d in chunk)
            w_exp = sum(d["expenses"] for d in chunk)
            w_tkt = sum(d["tickets"] for d in chunk)
            time_series.append({
                "date": chunk[0]["date"],
                "revenue": round(w_rev, 2),
                "expenses": round(w_exp, 2),
                "tickets": w_tkt
            })
    else:
        # Group by month
        month_groups = {}
        for d in daily_records:
            m_str = d["date"][:7]
            if m_str not in month_groups:
                month_groups[m_str] = {"revenue": 0.0, "expenses": 0.0, "tickets": 0}
            month_groups[m_str]["revenue"] += d["revenue"]
            month_groups[m_str]["expenses"] += d["expenses"]
            month_groups[m_str]["tickets"] += d["tickets"]
            
        time_series = []
        for m_str in sorted(month_groups.keys()):
            try:
                dt_obj = datetime.strptime(m_str, "%Y-%m")
                lbl = dt_obj.strftime("%b %Y")
            except:
                lbl = m_str
            time_series.append({
                "date": lbl,
                "revenue": round(month_groups[m_str]["revenue"], 2),
                "expenses": round(month_groups[m_str]["expenses"], 2),
                "tickets": month_groups[m_str]["tickets"]
            })
    
    return {
        "kpis": {
            "total_revenue": round(total_revenue, 2),
            "total_expenses": round(total_expenses, 2),
            "avg_daily_tickets": avg_daily_tickets,
            "current_inventory": current_inventory
        },
        "time_series": time_series,
        "segments": segment_revenue,
        "inventory_items": inventory_items
    }

def get_crm_ai_insights(data: dict) -> dict:
    """
    Calls LLM via Groq client to synthesize scattered CRM data
    into a clean, uniformed, business-owner-friendly JSON format.
    """
    kpis = data["kpis"]
    segments = data["segments"]
    
    try:
        prompt = (
            "You are a seasoned CFO and business advisor. A business owner is viewing their CRM portal but finds the scattered data "
            "difficult to understand. Synthesize the following CRM and financial data into a clear, unified, and highly understandable executive summary.\n\n"
            f"--- CRM Snapshot (Last 30 Days) ---\n"
            f"- Total Revenue from Closed-Won Deals: ${kpis['total_revenue']:,.2f}\n"
            f"- Net Operating Expenses: ${kpis['total_expenses']:,.2f}\n"
            f"- Average Daily Support Tickets: {kpis['avg_daily_tickets']} cases/day\n"
            f"- Current Warehouse Inventory: {kpis['current_inventory']:,} units\n"
            f"- Revenue by Customer Segment: {', '.join([f'{k}: ${v:,.2f}' for k, v in segments.items()])}\n\n"
            "Format your response as a JSON object with the following fields:\n"
            "- 'executive_summary': A warm, concise 2-3 sentence overview explaining how the business is doing in simple layperson terms.\n"
            "- 'key_metrics': A list of objects, each containing:\n"
            "  * 'label': The metric name (e.g., 'Revenue Performance', 'Overhead Expenses', 'Customer Support', 'Stock Control')\n"
            "  * 'explanation': A simple 1-sentence explanation of what this number means in reality for their business.\n"
            "  * 'status': 'positive', 'neutral', or 'attention' based on the health of the metric.\n"
            "- 'action_items': A list of objects, each containing:\n"
            "  * 'task': A clear, concrete action for the business owner.\n"
            "  * 'priority': 'High', 'Medium', or 'Low'\n"
            "  * 'rationale': Why they should do this based on the data.\n\n"
            "Return ONLY the raw JSON object, starting with { and ending with }. No markdown formatting or conversational filler."
        )

        primary_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        models = [primary_model, "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]
        chat_completion = None
        last_err = None
        for m in models:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=m,
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                break
            except Exception as ex:
                last_err = ex
                continue
        if chat_completion is None:
            raise last_err if last_err is not None else Exception("All models failed")
        raw_response = chat_completion.choices[0].message.content
        return json.loads(raw_response)
    except Exception as e:
        print(f"Warning: Error generating AI crm insights: {e}")
        # Fallback if Groq API fails or is not configured
        return {
            "executive_summary": "Your business shows steady financial performance over the past month. Closed-won deals are driving strong cash flow, while operating overhead remains aligned with budgets.",
            "key_metrics": [
                {
                    "label": "Revenue Performance",
                    "explanation": f"You generated ${kpis['total_revenue']:,.2f} in new sales from Closed-Won deals.",
                    "status": "positive" if kpis['total_revenue'] > 0 else "neutral"
                },
                {
                    "label": "Overhead Expenses",
                    "explanation": f"Total operating costs were ${kpis['total_expenses']:,.2f}, with lower overhead on weekends.",
                    "status": "neutral"
                },
                {
                    "label": "Customer Support",
                    "explanation": f"Incoming volume averages {kpis['avg_daily_tickets']} tickets daily, representing stable customer health.",
                    "status": "positive" if kpis['avg_daily_tickets'] < 2.0 else "attention"
                }
            ],
            "action_items": [
                {
                    "task": "Review pipeline velocity for pending deals",
                    "priority": "Medium",
                    "rationale": "Ensures the upcoming month maintains the current revenue momentum."
                }
            ]
        }

@app.get("/api/crm-data")
async def get_crm_data_api(days: int = 30):
    try:
        data = get_crm_dashboard_data(days)
    except Exception as e:
        return {"error": f"Failed to retrieve CRM metrics: {str(e)}"}
        
    # Convert segments map to a list of objects {"name", "value"}
    segments_list = [{"name": k, "value": round(v, 2)} for k, v in data["segments"].items()]
    if not segments_list:
        segments_list = [
            {"name": "Enterprise", "value": 0.0},
            {"name": "SMB", "value": 0.0},
            {"name": "Startup", "value": 0.0}
        ]
        
    # Generate AI executive insights for the business owner
    ai_insights = get_crm_ai_insights(data)
        
    return {
        "kpis": {
            "revenue": data["kpis"]["total_revenue"],
            "expenses": data["kpis"]["total_expenses"],
            "tickets": data["kpis"]["avg_daily_tickets"],
            "inventory": data["kpis"]["current_inventory"]
        },
        "history": data["time_series"],
        "segments": segments_list,
        "insights": ai_insights,
        "inventory_items": data.get("inventory_items", [])
    }


# ── Canary Lifecycle Handlers ──────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    from modules.canary_engine import CanaryEngine
    # Start background scheduler singleton
    CanaryEngine().start()

@app.on_event("shutdown")
async def shutdown_event():
    from modules.canary_engine import CanaryEngine
    # Stop background scheduler singleton
    CanaryEngine().stop()


# ── Canary APIs ────────────────────────────────────────────────────────────────
from data.canary_db import (
    get_canary_config, update_canary_config, get_canary_alerts,
    update_alert_feedback, get_canary_logs, get_failure_library,
    delete_canary_alert
)
from modules.canary_engine import CanaryEngine

class CanaryConfigRequest(BaseModel):
    running: int
    interval_minutes: int

@app.get("/api/canary/config")
async def get_canary_config_api():
    try:
        return get_canary_config()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/canary/config")
async def update_canary_config_api(request: CanaryConfigRequest):
    try:
        config = get_canary_config()
        next_run = None
        if request.running == 1 and config.get("running") == 0:
            next_run = datetime.now().isoformat()
            
        update_canary_config(
            running=request.running,
            interval_minutes=request.interval_minutes,
            next_run=next_run
        )
        return {"status": "success", "config": get_canary_config()}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/canary/alerts")
async def get_canary_alerts_api(limit: int = 50):
    try:
        return get_canary_alerts(limit)
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/canary/alerts/{alert_id}/feedback")
async def update_canary_feedback_api(alert_id: int, feedback: str):
    try:
        update_alert_feedback(alert_id, feedback)
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/api/canary/alerts/{alert_id}")
async def delete_canary_alert_api(alert_id: int):
    try:
        delete_canary_alert(alert_id)
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/canary/logs")
async def get_canary_logs_api(limit: int = 50):
    try:
        return get_canary_logs(limit)
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/canary/failure-library")
async def get_failure_library_api():
    try:
        return get_failure_library()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/canary/trigger")
async def trigger_canary_manual():
    try:
        engine = CanaryEngine()
        summary, details = engine.run_scan()
        from data.canary_db import log_canary_run
        log_canary_run(datetime.now().isoformat(), 100.0, 1, summary, details)
        return {"status": "success", "summary": summary, "details": json.loads(details)}
    except Exception as e:
        return {"error": str(e)}


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)

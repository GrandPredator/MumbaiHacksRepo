from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ledger import SatyaLedger
from agent_core import run_satya_scan
import json
from datetime import datetime

app = FastAPI(title="SatyaChain API")
blockchain = SatyaLedger()

# CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClaimRequest(BaseModel):
    claim: str

@app.post("/verify_and_log")
def verify_claim(payload: ClaimRequest):
    print(f"Received claim: {payload.claim}")
    
    # 1. Run Agentic AI
    ai_result = run_satya_scan(payload.claim)
    
    if "error" in ai_result:
        raise HTTPException(status_code=500, detail=ai_result["error"])

    # 2. Mine Block
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block['proof'])
    
    # 3. Add to Chain
    block = blockchain.create_block(
        proof=proof,
        previous_hash=blockchain.hash(last_block),
        data=ai_result
    )

    return {
        "satya_score": ai_result,
        "blockchain_record": {
            "index": block['index'],
            "hash": blockchain.hash(block),
            "timestamp": block['timestamp'],
            "previous_hash": block['previous_hash']
        }
    }

# --- THE NEW VISUAL CHAIN EXPLORER ---
@app.get("/chain", response_class=HTMLResponse)
def get_chain_visual():
    chain_data = blockchain.chain
    
    # CSS for the Dark Mode "Chain" Look
    html_content = """
    <html>
    <head>
        <title>SatyaChain Ledger Explorer</title>
        <style>
            body { background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; padding: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { color: #10b981; font-size: 2.5rem; margin: 0; }
            .header p { color: #64748b; }
            
            /* The Chain Connector */
            .chain-wrapper { display: flex; flex-direction: column; align-items: center; }
            .link-arrow { color: #334155; font-size: 24px; margin: 10px 0; }
            
            /* The Block Card */
            .block-card { 
                background: #1e293b; 
                border: 1px solid #334155; 
                border-radius: 12px; 
                padding: 20px; 
                width: 100%; 
                position: relative;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
                transition: transform 0.2s;
            }
            .block-card:hover { transform: scale(1.02); border-color: #10b981; }
            
            /* Genesis Block Style */
            .genesis { border-color: #3b82f6; }
            .genesis h2 { color: #3b82f6 !important; }

            /* Block Content */
            .block-header { display: flex; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 10px; }
            .block-index { font-family: monospace; font-size: 1.2rem; font-weight: bold; color: #10b981; }
            .timestamp { color: #94a3b8; font-size: 0.9rem; }
            
            .data-section { background: #0f172a; padding: 10px; rounded: 8px; font-family: monospace; font-size: 0.85rem; color: #cbd5e1; overflow-x: auto; }
            .verdict-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem; margin-bottom: 8px; }
            .verdict-verified { background: rgba(16, 185, 129, 0.2); color: #34d399; }
            .verdict-fake { background: rgba(244, 63, 94, 0.2); color: #fb7185; }

            .hash-row { margin-top: 15px; font-size: 0.8rem; color: #64748b; word-break: break-all; }
            .hash-label { color: #475569; font-weight: bold; display: block; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⛓️ Immutable Ledger</h1>
                <p>Live Blockchain Explorer • Node #1</p>
            </div>
            <div class="chain-wrapper">
    """

    for i, block in enumerate(chain_data):
        # Format Timestamp
        ts = datetime.fromtimestamp(block['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        
        # Handle Data Display (Genesis vs Verification)
        data_html = ""
        is_genesis = block['index'] == 1
        
        if is_genesis:
            data_html = f"<div style='color: #3b82f6; font-weight: bold;'>🚀 {block['data']}</div>"
            card_class = "block-card genesis"
        else:
            # Parse the SatyaScore data
            data = block['data']
            verdict = data.get('verdict', 'UNKNOWN')
            score = data.get('trust_score', 0)
            summary = data.get('claim_summary', 'No summary')
            
            verdict_class = "verdict-verified" if score > 70 else "verdict-fake"
            data_html = f"""
                <div class='verdict-badge {verdict_class}'>{verdict} (Score: {score})</div>
                <div style='margin-bottom: 5px;'><strong>Claim:</strong> {summary}</div>
            """
            card_class = "block-card"

        # Build the HTML for this block
        block_html = f"""
            <div class="{card_class}">
                <div class="block-header">
                    <span class="block-index">BLOCK #{block['index']}</span>
                    <span class="timestamp">{ts}</span>
                </div>
                <div class="data-section">
                    {data_html}
                </div>
                <div class="hash-row">
                    <span class="hash-label">PREV HASH:</span> {block['previous_hash']}
                </div>
                <div class="hash-row">
                    <span class="hash-label">CURRENT HASH:</span> <span style="color: #cbd5e1;">{blockchain.hash(block)}</span>
                </div>
                <div class="hash-row">
                    <span class="hash-label">NONCE (PROOF):</span> {block['proof']}
                </div>
            </div>
        """
        
        html_content += block_html
        
        # Add arrow if not the last block
        if i < len(chain_data) - 1:
            html_content += "<div class='link-arrow'>⬇</div>"

    html_content += """
            </div>
            <div style="text-align: center; margin-top: 40px; color: #334155;">
                <p>End of Chain</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# Optional: Keep the JSON version for raw debugging if needed
@app.get("/chain/raw")
def get_chain_json():
    return {"chain": blockchain.chain, "length": len(blockchain.chain)}
from flask import Flask, render_template_string, request, jsonify
import anthropic
import json
from datetime import datetime

app = Flask(__name__)
client = anthropic.Anthropic()

# HTML Template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ComplianceGuard - AI Compliance Auditor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --neon-cyan: #00d4ff;
            --neon-green: #39ff14;
            --dark-bg: #0a0e27;
            --darker-bg: #050810;
            --card-bg: #1a1f3a;
            --text-light: #e0e0e0;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, var(--darker-bg) 0%, var(--dark-bg) 100%);
            color: var(--text-light);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            border-bottom: 2px solid var(--neon-cyan);
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        }
        
        h1 {
            font-size: 2.5em;
            color: var(--neon-cyan);
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.8);
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: var(--neon-green);
            font-size: 1.1em;
        }
        
        .input-section {
            background: var(--card-bg);
            padding: 30px;
            border: 2px solid var(--neon-cyan);
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 0 30px rgba(0, 212, 255, 0.2);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: var(--neon-green);
            margin-bottom: 10px;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.9em;
        }
        
        textarea {
            width: 100%;
            padding: 15px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--neon-cyan);
            color: var(--text-light);
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            min-height: 150px;
            resize: vertical;
        }
        
        textarea:focus {
            outline: none;
            border-color: var(--neon-green);
            box-shadow: 0 0 20px rgba(57, 255, 20, 0.3);
        }
        
        .checkbox-group {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .checkbox-item {
            display: flex;
            align-items: center;
        }
        
        input[type="checkbox"] {
            margin-right: 10px;
            cursor: pointer;
            width: 18px;
            height: 18px;
        }
        
        .checkbox-item label {
            margin: 0;
            display: inline;
            text-transform: none;
            font-weight: normal;
            font-size: 1em;
        }
        
        button {
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-green));
            color: var(--darker-bg);
            padding: 15px 40px;
            border: none;
            border-radius: 4px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
            width: 100%;
        }
        
        button:hover {
            box-shadow: 0 0 40px rgba(0, 212, 255, 0.8), 0 0 60px rgba(57, 255, 20, 0.4);
            transform: scale(1.02);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .loading {
            text-align: center;
            color: var(--neon-cyan);
            font-size: 1.2em;
            margin: 20px 0;
        }
        
        .spinner {
            border: 3px solid rgba(0, 212, 255, 0.3);
            border-top: 3px solid var(--neon-cyan);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 10px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results-section {
            background: var(--card-bg);
            padding: 30px;
            border: 2px solid var(--neon-green);
            border-radius: 8px;
            box-shadow: 0 0 30px rgba(57, 255, 20, 0.2);
        }
        
        .results-section h2 {
            color: var(--neon-green);
            margin-bottom: 20px;
            text-transform: uppercase;
            font-size: 1.5em;
        }
        
        .report-section {
            margin-bottom: 25px;
            padding: 20px;
            background: rgba(0, 212, 255, 0.05);
            border-left: 4px solid var(--neon-cyan);
            border-radius: 4px;
        }
        
        .report-section h3 {
            color: var(--neon-cyan);
            margin-bottom: 12px;
        }
        
        .violation {
            background: rgba(255, 0, 0, 0.1);
            border-left: 3px solid #ff4444;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        
        .gap {
            background: rgba(255, 165, 0, 0.1);
            border-left: 3px solid #ffaa00;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        
        .remediation {
            background: rgba(57, 255, 20, 0.1);
            border-left: 3px solid var(--neon-green);
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        
        .download-btn {
            background: linear-gradient(135deg, var(--neon-green), var(--neon-cyan));
            margin-top: 20px;
        }
        
        .error {
            background: rgba(255, 0, 0, 0.1);
            border: 2px solid #ff4444;
            color: #ffaaaa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .success {
            background: rgba(57, 255, 20, 0.1);
            border: 2px solid var(--neon-green);
            color: var(--neon-green);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ COMPLIANCEGUARD</h1>
            <p class="subtitle"># AI-Powered Compliance Audit Tool</p>
        </header>
        
        <div class="input-section">
            <form id="auditForm">
                <div class="form-group">
                    <label for="documentation">📄 Paste Your Documentation/Code/Policies</label>
                    <textarea id="documentation" name="documentation" placeholder="Paste your security policies, code snippets, infrastructure documentation, or any compliance-related content here..." required></textarea>
                </div>
                
                <div class="form-group">
                    <label>🔍 Select Compliance Frameworks to Check</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="gdpr" name="frameworks" value="GDPR" checked>
                            <label for="gdpr">GDPR</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="ccpa" name="frameworks" value="CCPA" checked>
                            <label for="ccpa">CCPA</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="hipaa" name="frameworks" value="HIPAA" checked>
                            <label for="hipaa">HIPAA</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="pcidss" name="frameworks" value="PCI-DSS" checked>
                            <label for="pcidss">PCI-DSS</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="nist" name="frameworks" value="NIST CSF">
                            <label for="nist">NIST CSF</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="iso27001" name="frameworks" value="ISO 27001">
                            <label for="iso27001">ISO 27001</label>
                        </div>
                    </div>
                </div>
                
                <button type="submit" id="submitBtn">🚀 RUN COMPLIANCE AUDIT</button>
            </form>
        </div>
        
        <div id="resultsContainer"></div>
    </div>
    
    <script>
        document.getElementById('auditForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const documentation = document.getElementById('documentation').value;
            const frameworks = Array.from(document.querySelectorAll('input[name="frameworks"]:checked'))
                .map(cb => cb.value);
            
            if (!documentation.trim()) {
                alert('Please enter documentation to audit');
                return;
            }
            
            if (frameworks.length === 0) {
                alert('Please select at least one compliance framework');
                return;
            }
            
            const resultsContainer = document.getElementById('resultsContainer');
            resultsContainer.innerHTML = '<div class="loading"><div class="spinner"></div><p>Analyzing compliance... This may take 30 seconds...</p></div>';
            
            try {
                const response = await fetch('/audit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        documentation: documentation,
                        frameworks: frameworks
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultsContainer.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                    return;
                }
                
                displayResults(data);
            } catch (error) {
                resultsContainer.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        });
        
        function displayResults(data) {
            const resultsContainer = document.getElementById('resultsContainer');
            
            let html = '<div class="results-section">';
            html += '<h2>📊 COMPLIANCE AUDIT REPORT</h2>';
            html += `<p style="margin-bottom: 20px; opacity: 0.8;">Generated: ${new Date().toLocaleString()}</p>`;
            
            // Violations
            if (data.violations && data.violations.length > 0) {
                html += '<div class="report-section">';
                html += '<h3>⚠️ VIOLATIONS FOUND (' + data.violations.length + ')</h3>';
                data.violations.forEach(v => {
                    html += `<div class="violation"><strong>${v.framework}:</strong> ${v.issue}</div>`;
                });
                html += '</div>';
            }
            
            // Gaps
            if (data.gaps && data.gaps.length > 0) {
                html += '<div class="report-section">';
                html += '<h3>🔍 COMPLIANCE GAPS (' + data.gaps.length + ')</h3>';
                data.gaps.forEach(g => {
                    html += `<div class="gap"><strong>${g.framework}:</strong> ${g.gap}</div>`;
                });
                html += '</div>';
            }
            
            // Remediations
            if (data.remediations && data.remediations.length > 0) {
                html += '<div class="report-section">';
                html += '<h3>✅ RECOMMENDED REMEDIATIONS</h3>';
                data.remediations.forEach(r => {
                    html += `<div class="remediation"><strong>Action:</strong> ${r}</div>`;
                });
                html += '</div>';
            }
            
            // Summary
            if (data.summary) {
                html += '<div class="report-section">';
                html += '<h3>📋 SUMMARY</h3>';
                html += `<p>${data.summary}</p>`;
                html += '</div>';
            }
            
            html += '</div>';
            resultsContainer.innerHTML = html;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/audit', methods=['POST'])
def audit():
    try:
        data = request.json
        documentation = data.get('documentation', '')
        frameworks = data.get('frameworks', [])
        
        if not documentation:
            return jsonify({'error': 'No documentation provided'}), 400
        
        # Create prompt for Claude
        prompt = f"""You are an expert compliance auditor. Analyze the following documentation/code/policies against these compliance frameworks: {', '.join(frameworks)}.

DOCUMENTATION TO AUDIT:
{documentation}

Provide a detailed compliance audit report with:

1. VIOLATIONS: List any direct violations found for each framework
2. GAPS: List missing controls or requirements
3. REMEDIATIONS: Provide specific, actionable steps to fix each issue
4. SUMMARY: Overall compliance posture (1-2 sentences)

Format your response as JSON with this structure:
{{
  "violations": [
    {{"framework": "FRAMEWORK_NAME", "issue": "description"}},
    ...
  ],
  "gaps": [
    {{"framework": "FRAMEWORK_NAME", "gap": "description"}},
    ...
  ],
  "remediations": [
    "action 1",
    "action 2",
    ...
  ],
  "summary": "overall assessment"
}}

Be thorough and specific. Focus on real compliance risks."""

        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Extract JSON from response
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
        except:
            result = {
                "violations": [],
                "gaps": [],
                "remediations": [],
                "summary": response_text
            }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

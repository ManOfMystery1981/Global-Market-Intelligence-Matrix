# pdf_generator.py - Professional PDF Generation with Jinja2 Templating
import os
import uuid
import json
from datetime import datetime
from weasyprint import HTML
from jinja2 import Template

class PDFReportGenerator:
    """Generate professional institutional-grade PDF reports using Jinja2 templating."""
    
    def __init__(self):
        self.template_str = self._load_template()
        self.template = Template(self.template_str)
    
    def _load_template(self):
        """Load the HTML template from Gemini with Jinja2 placeholders."""
        return """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {
        size: A4;
        margin: 22mm 18mm;
        background-color: #ffffff;
        @bottom-right {
            content: "Page " counter(page) " of " counter(pages);
            font-family: 'Georgia', serif;
            font-size: 8pt;
            color: #64748b;
        }
        @bottom-left {
            content: "Autonomous Data Refinery • GLOBAL MARKET INTELLIGENCE MATRIX";
            font-family: 'Georgia', serif;
            font-size: 8pt;
            color: #64748b;
        }
    }
    
    *, *::before, *::after { box-sizing: border-box; }
    
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #0f172a;
        background-color: #ffffff;
        line-height: 1.6;
        font-size: 10.5pt;
        margin: 0;
        padding: 0;
    }
    
    .cover-page {
        padding: 55px 35px;
        background: linear-gradient(135deg, #0f172a 0%, #1a2744 100%);
        color: #ffffff;
        border-radius: 4px;
        margin-bottom: 45px;
        border-left: 6px solid #8b5cf6;
        border-right: 6px solid #10b981;
    }
    
    .cover-title {
        font-family: 'Georgia', serif;
        font-size: 24pt;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 12px 0;
        color: #10b981;
    }
    
    .cover-subtitle {
        font-size: 12pt;
        font-weight: 300;
        color: #94a3b8;
        margin-bottom: 35px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metadata-box {
        display: table;
        width: 100%;
        border-top: 1px solid #334155;
        padding-top: 20px;
    }
    
    .metadata-cell {
        display: table-cell;
        width: 33.33%;
        font-size: 9.5pt;
        color: #cbd5e1;
    }
    
    .metadata-cell strong { color: #8b5cf6; }
    
    h1 {
        font-family: 'Georgia', serif;
        font-size: 16pt;
        font-weight: bold;
        color: #0f172a;
        text-transform: uppercase;
        margin-top: 40px;
        margin-bottom: 15px;
        border-bottom: 2px solid #0f172a;
        padding-bottom: 5px;
        page-break-after: avoid;
    }
    
    h2 {
        font-family: 'Georgia', serif;
        font-size: 13pt;
        font-weight: bold;
        color: #1e1e2f;
        border-left: 4px solid #8b5cf6;
        padding-left: 12px;
        margin-top: 30px;
        margin-bottom: 12px;
        page-break-after: avoid;
    }
    
    h3 {
        font-family: 'Georgia', serif;
        font-size: 11pt;
        font-weight: bold;
        color: #0f172a;
        margin-top: 20px;
        margin-bottom: 10px;
        page-break-after: avoid;
    }
    
    p {
        margin-top: 0;
        margin-bottom: 15px;
        text-align: justify;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 30px;
        font-size: 9.5pt;
        page-break-inside: avoid;
    }
    
    th {
        background-color: #0f172a;
        color: #ffffff;
        font-weight: bold;
        text-align: left;
        padding: 10px 12px;
        border: 1px solid #1e293b;
    }
    
    td {
        padding: 8px 12px;
        border: 1px solid #e2e8f0;
    }
    
    tr:nth-child(even) td { background-color: #f8fafc; }
    
    .pos-delta { color: #059669; font-weight: bold; }
    .neg-delta { color: #dc2626; font-weight: bold; }
    
    .bullet-list { margin-bottom: 25px; padding-left: 0; }
    
    .bullet-item {
        list-style-type: none;
        position: relative;
        padding-left: 22px;
        margin-bottom: 12px;
        text-align: justify;
    }
    
    .bullet-item::before {
        content: "◆";
        position: absolute;
        left: 0;
        color: #8b5cf6;
        font-size: 10pt;
        top: 1px;
    }
    
    .bullet-item-square {
        list-style-type: none;
        position: relative;
        padding-left: 22px;
        margin-bottom: 12px;
        text-align: justify;
    }
    
    .bullet-item-square::before {
        content: "▪";
        position: absolute;
        left: 0;
        color: #10b981;
        font-size: 12pt;
        top: -1px;
    }
    
    .blockquote {
        background-color: #f5f3ff;
        border-left: 4px solid #8b5cf6;
        padding: 15px 20px;
        margin: 25px 0;
        font-style: italic;
        border-radius: 0 4px 4px 0;
        page-break-inside: avoid;
    }
    
    .diagram-box {
        border: 1px solid #cbd5e1;
        background-color: #f8fafc;
        padding: 15px;
        text-align: center;
        font-family: monospace;
        font-size: 9.5pt;
        color: #334155;
        margin: 20px 0;
        border-radius: 4px;
        page-break-inside: avoid;
    }
    
    .watermark {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-45deg);
        font-size: 72pt;
        color: rgba(139, 92, 246, 0.05);
        font-weight: bold;
        letter-spacing: 8px;
        pointer-events: none;
        z-index: 9999;
    }
    
    .value-highlight {
        background-color: #10b981;
        color: #ffffff;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
</head>
<body>

<div class="watermark">CONFIDENTIAL</div>

<div class="page-container">

    <div class="cover-page">
        <div class="cover-title">Global Market Intelligence Matrix</div>
        <div class="cover-subtitle">Autonomous Data Refinery • Enterprise Strategic Audit</div>
        <div class="metadata-box">
            <div class="metadata-cell"><strong>Client:</strong> {{ client_name }}</div>
            <div class="metadata-cell"><strong>Issuance:</strong> {{ generation_date }}</div>
            <div class="metadata-cell" style="text-align: right;"><strong>Control DCN:</strong> {{ control_id }}</div>
        </div>
    </div>

    <h1>Executive Summary & Macro Aligned Mapping</h1>
    
    <h2>Current State Assessment & Operational Baseline</h2>
    <p>{{ executive_summary }}</p>

    <h2>Data Synthesis & Real-Time Automation Infrastructure</h2>
    <p>{{ data_synthesis }}</p>

    <div class="diagram-box">
[ Live Extraction Bots ] ──► [ Automated Ingestion Engine ] ──► [ Predictive Risk Node ]
                                                                     │
[ High-Yield Optimization ] ◄── [ Quantitative Synthesis Matrix ] ◄──┘
    </div>

    <h1>Deep-Dive Analytical Modules</h1>

    <h2>Module I: Systemic Diagnostic Audit & Risk Isolation</h2>
    
    <h3>Granular Operational Infrastructure Breakdown</h3>
    <p>{{ infrastructure_breakdown }}</p>
    
    <div class="bullet-list">
        <div class="bullet-item"><strong>Structural Friction Analysis:</strong> {{ friction_analysis }}</div>
        <div class="bullet-item"><strong>Asset Allocation Velocity:</strong> {{ asset_velocity }}</div>
        <div class="bullet-item"><strong>Systemic Bottlenecks:</strong> {{ systemic_bottlenecks }}</div>
    </div>

    <h3>Stress-Testing & Market Volatility Modeling</h3>
    <p>{{ stress_testing }}</p>

    <table>
        <thead>
            <tr>
                <th>Diagnostic Vector</th>
                <th>Identified Exposure Level</th>
                <th>Quantified Financial Impact</th>
                <th>Priority Score</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Operational Workflow Pipeline</strong></td>
                <td>{{ op_exposure_level }}</td>
                <td>{{ op_financial_impact }}</td>
                <td>{{ op_priority_score }}</td>
            </tr>
            <tr>
                <td><strong>Resource Allocation Velocity</strong></td>
                <td>{{ res_exposure_level }}</td>
                <td>{{ res_financial_impact }}</td>
                <td>{{ res_priority_score }}</td>
            </tr>
            <tr>
                <td><strong>Infrastructure Scalability Metrics</strong></td>
                <td>{{ infra_exposure_level }}</td>
                <td>{{ infra_financial_impact }}</td>
                <td>{{ infra_priority_score }}</td>
            </tr>
        </tbody>
    </table>

    <div class="blockquote">
        <strong>Strategic Directive:</strong> {{ strategic_directive }}
    </div>

    <h2>Module II: Implementation & Governance Framework</h2>

    <h3>Phased Execution Roadmap & Integration Sprints</h3>
    <p>{{ execution_roadmap }}</p>

    <div class="diagram-box">
[ PHASE I: CORE INTEGRATION ] ──► [ PHASE II: CALIBRATION ] ──► [ PHASE III: AUTONOMOUS HANDOVER ]
       (Days 1 - 15)                      (Days 16 - 30)                    (Days 31+)
    </div>

    <div class="bullet-list">
        <div class="bullet-item-square"><strong>Phase I: Core Integration (Days 1–15):</strong> {{ phase_i }}</div>
        <div class="bullet-item-square"><strong>Phase II: Optimization & Calibration (Days 16–30):</strong> {{ phase_ii }}</div>
        <div class="bullet-item-square"><strong>Phase III: Full Autonomy Handover (Days 31+):</strong> {{ phase_iii }}</div>
    </div>

    <h3>Automated Governance & Compliance Guardrails</h3>
    <p>{{ governance_guardrails }}</p>

    <h1>Legal Protocols & Commercial Disclosures</h1>
    
    <div class="blockquote" style="background-color: #f8fafc; border-left-color: #64748b;">
        <strong>Proprietary Covenant Notice:</strong> {{ proprietary_notice }}
    </div>
    
    <p style="font-size: 9pt; color: #475569;"><strong>Limitation of Liability:</strong> {{ liability_limitation }}</p>

    <h1>The Premium Valuation Matrix</h1>
    <table>
        <thead>
            <tr>
                <th>Deliverable Attribute</th>
                <th>Traditional Legacy Agency Standard ($5,000+)</th>
                <th>Your Automated Framework ($1,000)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Onboarding Latency</strong></td>
                <td>2–4 weeks of manual consulting and interviews.</td>
                <td class="pos-delta">Instantaneous ingestion via direct pipeline hooks.</td>
            </tr>
            <tr>
                <td><strong>Data Freshness Profile</strong></td>
                <td>Stale historical samples.</td>
                <td class="pos-delta">Live, real-time programmatic database queries.</td>
            </tr>
            <tr>
                <td><strong>Deployment Turnaround</strong></td>
                <td>3 to 6 months of bloated hourly consulting billing.</td>
                <td class="pos-delta">Accelerated 30-day structural rollout blueprint.</td>
            </tr>
            <tr>
                <td><strong>Capital Efficiency Ratio</strong></td>
                <td>High friction financial entry barrier.</td>
                <td class="pos-delta">Elite enterprise consulting at an accessible price.</td>
            </tr>
        </tbody>
    </table>

    <p style="text-align: center; font-size: 8pt; color: #64748b; margin-top: 40px;">
        © 2026 Autonomous Data Refinery. Powered by Automated Bot Infrastructure. All rights reserved.
    </p>

</div>

</body>
</html>"""
    
    def generate_report(self, data, output_path=None):
        """Generate a PDF report from data using Jinja2 templating."""
        if output_path is None:
            output_path = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Prepare the data with defaults
        report_data = {
            'client_name': data.get('client', 'Institutional Client'),
            'generation_date': datetime.now().strftime('%B %d, %Y at %H:%M UTC'),
            'control_id': str(uuid.uuid4())[:8].upper(),
            
            # Content sections
            'executive_summary': data.get('executive_summary', 'No executive summary provided.'),
            'data_synthesis': data.get('data_synthesis', 'No data synthesis provided.'),
            'infrastructure_breakdown': data.get('infrastructure_breakdown', 'No infrastructure breakdown provided.'),
            'friction_analysis': data.get('friction_analysis', 'No friction analysis provided.'),
            'asset_velocity': data.get('asset_velocity', 'No asset velocity data provided.'),
            'systemic_bottlenecks': data.get('systemic_bottlenecks', 'No bottlenecks identified.'),
            'stress_testing': data.get('stress_testing', 'No stress testing data provided.'),
            'strategic_directive': data.get('strategic_directive', 'No strategic directive provided.'),
            'execution_roadmap': data.get('execution_roadmap', 'No execution roadmap provided.'),
            'governance_guardrails': data.get('governance_guardrails', 'No governance guardrails provided.'),
            'proprietary_notice': data.get('proprietary_notice', 'Proprietary notice not provided.'),
            'liability_limitation': data.get('liability_limitation', 'Liability limitation not provided.'),
            
            # Phase descriptions
            'phase_i': data.get('phase_i', 'Global rollout of foundational structural parameters.'),
            'phase_ii': data.get('phase_ii', 'Precision tuning of system infrastructure hooks.'),
            'phase_iii': data.get('phase_iii', 'Deep automated stress-testing and validation.'),
            
            # Table data
            'op_exposure_level': data.get('op_exposure_level', 'Medium'),
            'op_financial_impact': data.get('op_financial_impact', '$250,000'),
            'op_priority_score': data.get('op_priority_score', 'High'),
            'res_exposure_level': data.get('res_exposure_level', 'Low'),
            'res_financial_impact': data.get('res_financial_impact', '$150,000'),
            'res_priority_score': data.get('res_priority_score', 'Medium'),
            'infra_exposure_level': data.get('infra_exposure_level', 'High'),
            'infra_financial_impact': data.get('infra_financial_impact', '$500,000'),
            'infra_priority_score': data.get('infra_priority_score', 'Critical'),
        }
        
        # Render the template
        html_content = self.template.render(**report_data)
        
        # Generate PDF
        HTML(string=html_content).write_pdf(output_path)
        
        return output_path
    
    def generate_report_from_json(self, json_file, output_path=None):
        """Generate a PDF report from a JSON file."""
        with open(json_file, 'r') as f:
            data = json.load(f)
        return self.generate_report(data, output_path)


# --- Integration with Your Existing Bots ---

def generate_professional_report(article_content, market_data, output_path=None):
    """
    Generate a professional PDF report from article content and market data.
    This integrates with your existing llm_analyst_bot and delivery_bot.
    """
    # Parse the article content into sections
    # This is a simplified example - you'd need to parse your actual article format
    sections = {
        'executive_summary': article_content[:500] if article_content else 'No content',
        'data_synthesis': 'Real-time data pipelines are now operational.',
        'infrastructure_breakdown': 'Your current infrastructure shows optimization potential.',
        # Add more sections as needed
    }
    
    # Merge with market data
    report_data = {**sections, **market_data}
    
    # Generate the PDF
    generator = PDFReportGenerator()
    return generator.generate_report(report_data, output_path)


if __name__ == "__main__":
    # Test the generator
    test_data = {
        'client': 'dsull1981@gmail.com',
        'executive_summary': 'This comprehensive analysis reveals significant arbitrage opportunities across multiple asset classes...',
        'data_synthesis': 'Real-time data pipelines are now operational with sub-second latency...',
        'infrastructure_breakdown': 'Your current infrastructure shows 23% optimization potential...',
        'friction_analysis': 'Operational friction is 12% above optimal threshold...',
        'asset_velocity': 'Asset velocity is 34% below industry benchmark...',
        'systemic_bottlenecks': '3 critical bottlenecks identified in the data ingestion layer...',
        'stress_testing': 'Market volatility modeling shows 15% downside risk...',
        'strategic_directive': 'Focus on eliminating micro-friction points to achieve 40% efficiency gains...',
        'execution_roadmap': '30-day rollout framework with weekly milestones...',
        'governance_guardrails': 'Automated compliance monitoring with real-time alerts...',
        'proprietary_notice': 'This document contains proprietary trade secrets...',
        'liability_limitation': 'All strategies are suggestions, not guarantees...',
    }
    
    generator = PDFReportGenerator()
    output = generator.generate_report(test_data)
    print(f"✅ PDF generated: {output}")

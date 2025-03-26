# ui/app.py
import sys
import os
import time
import json
import base64
from pathlib import Path
import streamlit as st

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.test_generator import TestGenerator
from core.change_detector import ChangeDetector
from config import settings

def main():
    st.set_page_config(
        page_title="AI Banking Test Suite Generator",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .stExpander {
        background: #f8f9fa;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stDownloadButton button {
        background: #4CAF50 !important;
        color: white !important;
    }
    .risk-high { color: #ff4b4b !important; font-weight: 700; }
    .risk-medium { color: #ffa600 !important; }
    .risk-low { color: #00c853 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = []
    
    # Sidebar
    with st.sidebar:
        st.title("Configuration ⚙️")
        uploaded_file = st.file_uploader("Upload Use Cases JSON", type=["json"])
        
        if uploaded_file:
            save_path = Path("config") / "current_config.json"
            save_path.parent.mkdir(exist_ok=True)
            
            with st.spinner("Saving configuration..."):
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Configuration updated!")
                st.session_state.results = []
        
        st.divider()
        if st.button("🔄 Start Context Monitoring"):
            try:
                detector = ChangeDetector(str(Path("config") / "current_config.json"))
                detector.start()
                st.toast("Context monitoring activated!", icon="✅")
            except Exception as e:
                st.error(f"Error starting monitor: {str(e)}")
    
    # Main Interface
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Test Generation 🚀")
        
        if st.button("Generate Test Suite", type="primary"):
            config_path = Path("config") / "current_config.json"
            if not config_path.exists():
                st.error("Please upload a config file first!")
                return
                
            try:
                with st.spinner("Generating AI-powered test cases..."):
                    generator = TestGenerator()
                    with open(config_path) as f:
                        use_cases = json.load(f)
                    
                    progress_bar = st.progress(0)
                    results = []
                    total_cases = sum(len(cases) for cases in use_cases.values())
                    processed = 0
                    
                    for category, cases in use_cases.items():
                        for case in cases:
                            try:
                                result = generator.generate_test_case(case)
                                result.update({
                                    'category': category,
                                    'risk_level': case.get('risk', 'High'),
                                    'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
                                })
                                results.append(result)
                            except Exception as e:
                                st.error(f"Failed to generate test case: {str(e)}")
                            processed += 1
                            progress_bar.progress(processed / total_cases)
                            time.sleep(0.1)
                    
                    st.session_state.results = results
                    st.success(f"✅ Generated {len(results)} context-aware test cases!")

            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
    
    with col2:
        st.header("Test Cases 📋")
        
        if not st.session_state.results:
            st.info("No test cases generated yet. Upload a config and click 'Generate Test Suite'")
        else:
            for idx, test_case in enumerate(st.session_state.results, 1):
                with st.expander(f"TC-{idx}: {test_case.get('use_case', 'Unnamed Case')}", expanded=True):
                    # Metadata columns
                    meta_col1, meta_col2, meta_col3 = st.columns([1,1,2])
                    
                    with meta_col1:
                        st.markdown(f"**🏦 Category**: {test_case.get('category', 'N/A')}")
                        st.markdown(f"**⚠️ Risk**: <span class='risk-{test_case.get('risk_level', 'high').lower()}'>{test_case.get('risk_level', 'High')}</span>", 
                                   unsafe_allow_html=True)
                        
                    with meta_col2:
                        st.markdown(f"**🆔 Test ID**: `{test_case.get('test_id', 'FINSEC-XXXX')}`")
                        st.markdown(f"**📅 Last Updated**: {test_case.get('last_updated', 'N/A')}")
                    
                    with meta_col3:
                        st.markdown("**🔍 Compliance References**")
                        for ref in test_case.get('compliance_references', []):
                            st.markdown(f"- {ref}")
                    
                    # Tabs for different test aspects
                    tab1, tab2, tab3 = st.tabs(["✅ Positive Flow", "❌ Negative Scenarios", "⚖️ Validation"])
                    
                    with tab1:
                        st.markdown("**Valid Transaction Scenario**")
                        if test_case.get('positive_scenario'):
                            for step in test_case['positive_scenario']:
                                st.markdown(f"- {step}")
                        else:
                            st.warning("No positive scenario generated")
                            
                        st.markdown("**Test Data Requirements**")
                        if test_case.get('test_data'):
                            for data in test_case['test_data']:
                                st.markdown(f"- `{data}`")
                        else:
                            st.info("No specific test data requirements")
                    
                    with tab2:
                        st.markdown("**Fraud/Exception Scenarios**")
                        if test_case.get('negative_scenarios'):
                            for scenario in test_case['negative_scenarios']:
                                st.markdown(f"- 🚨 {scenario}")
                        else:
                            st.warning("No negative scenarios generated")
                        
                        st.markdown("**Edge Cases**")
                        if test_case.get('edge_cases'):
                            for edge in test_case['edge_cases']:
                                st.markdown(f"- ⚠️ {edge}")
                        else:
                            st.info("No edge cases identified")
                    
                    with tab3:
                        val_col1, val_col2 = st.columns(2)
                        with val_col1:
                            st.markdown("**Validation Criteria**")
                            if test_case.get('validation_criteria'):
                                for criteria in test_case['validation_criteria']:
                                    st.markdown(f"- ✔️ {criteria}")
                            else:
                                st.info("No validation criteria specified")
                        
                        with val_col2:
                            st.markdown("**System Context**")
                            if test_case.get('system_context'):
                                for ctx in test_case['system_context']:
                                    st.markdown(f"- 🔗 {ctx}")
                            else:
                                st.info("No system context available")
                    
                    # Download button
                    st.download_button(
                        label=f"📥 Download TC-{idx}",
                        data=json.dumps(test_case, indent=2),
                        file_name=f"test_case_{test_case.get('test_id', idx)}.json",
                        mime="application/json",
                        key=f"download_{idx}"
                    )
            
            # Full report download
            st.divider()
            if st.button("📦 Download Full Test Suite Report"):
                report_data = json.dumps(st.session_state.results, indent=2)
                b64 = base64.b64encode(report_data.encode()).decode()
                
                st.markdown(
                    f'<a href="data:application/json;base64,{b64}" download="full_test_suite.json" style="display: inline-block; padding: 0.5rem 1rem; background: #4CAF50; color: white; border-radius: 0.5rem; text-decoration: none;">Download Full Report</a>',
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    main()
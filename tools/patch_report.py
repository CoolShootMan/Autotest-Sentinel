import os
import re
import sys

# Add tools dir to path so we can import diagnose_failed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagnose_failed import extract_failed_cases, find_latest_allure_dir

html_path = r"D:\monster_test\Autotest-monster\report\Error_Test_Case_Diagnosis_Report_20260522_142645.html"

print("Finding correct order using extract_failed_cases...")
allure_dir = find_latest_allure_dir()
if allure_dir:
    results = extract_failed_cases(allure_dir)
    ordered_case_names = [r["name"] for r in results]
    print("Correct order:", ordered_case_names)
else:
    print("Could not find allure dir. Skipping reordering.")
    ordered_case_names = []

print("Reading HTML file...")
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

print("Patching CSS...")
css_old = ".data-table td { padding: 8px 12px; border-bottom: 1px solid #eee; }"
css_old2 = ".data-table td { padding: 8px 12px; border-bottom: 1px solid #eee; word-break: break-all; }"
css_new = ".data-table td { padding: 8px 12px; border-bottom: 1px solid #eee; word-break: break-word; overflow-wrap: anywhere; }"

if css_old in content:
    content = content.replace(css_old, css_new)
elif css_old2 in content:
    content = content.replace(css_old2, css_new)
elif ".data-table td" in content and "break-word" not in content:
    content = re.sub(r'\.data-table td \{[^\}]+\}', css_new, content)

js_fix = """<script>
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.case-section').forEach(section => {
        let h3 = section.querySelector('h3');
        if(h3 && h3.innerText.includes('Step-by-Step') && !section.querySelector('button.collapse-btn')) {
            let btn = document.createElement('button');
            btn.className = 'collapse-btn';
            btn.innerHTML = 'Collapse &#x25B2;';
            btn.style.cssText = 'background: #e3f2fd; color: #1e88e5; border: 1px solid #90caf9; border-radius: 4px; padding: 6px 12px; cursor: pointer; font-size: 13px; font-weight: bold; float: right; margin-top:-30px;';
            h3.parentNode.insertBefore(btn, h3.nextSibling);
            
            // Collect all step records in this case-section
            // Some might be wrapped in steps-container
            let container = section.querySelector('.steps-container');
            let records = section.querySelectorAll('.step-record');
            btn.onclick = function() {
                if (container) {
                    let isHidden = container.style.display === 'none';
                    container.style.display = isHidden ? 'block' : 'none';
                    this.innerHTML = isHidden ? 'Collapse &#x25B2;' : 'Expand &#x25BC;';
                } else {
                    let isHidden = records[0].style.display === 'none';
                    records.forEach(r => r.style.display = isHidden ? 'block' : 'none');
                    this.innerHTML = isHidden ? 'Collapse &#x25B2;' : 'Expand &#x25BC;';
                }
            };
        }
    });
});
</script>
</body>"""

if "Collapse" not in content and "collapse-btn" not in content:
    content = content.replace("</body>", js_fix)
    print("Injected JS for buttons.")

if ordered_case_names:
    print("Reordering case sections in HTML...")
    # Find where cases start. Usually after <div class="summary-section">...</div>
    # The first case section starts with <div class="case-section"
    # Let's split by <div class="case-section"
    parts = content.split('<div class="case-section"')
    if len(parts) > 1:
        header = parts[0]
        cases_dict = {}
        for part in parts[1:]:
            # Find the Case name
            # <h2>Case: test_name</h2>
            m = re.search(r'<h2>Case:\s*([^<]+)</h2>', part)
            if m:
                cname = m.group(1).strip()
                cases_dict[cname] = '<div class="case-section"' + part
            else:
                # If cannot find case name, append to header
                header += '<div class="case-section"' + part
        
        # Rebuild content
        new_content = header
        for cname in ordered_case_names:
            if cname in cases_dict:
                new_content += cases_dict[cname]
                del cases_dict[cname]
        
        # Add any remaining cases that weren't in ordered_case_names
        for part in cases_dict.values():
            new_content += part
            
        content = new_content
        print("Reordering complete.")

print("Saving patched HTML...")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done patching.")

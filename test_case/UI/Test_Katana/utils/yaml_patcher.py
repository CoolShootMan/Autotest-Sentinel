import os
import re
from loguru import logger

def patch_yaml_step(file_path, test_case_id, step_key, new_locator):
    """
    Safely patch a specific step in a YAML file using regex to preserve comments and formatting.
    """
    if not os.path.exists(file_path):
        logger.error(f"Patcher: File not found: {file_path}")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Find the test case block
    # Matches "testTxxxx:" followed by everything until the next top-level key or EOF
    # We use a non-greedy match for the block content
    case_pattern = rf"^({test_case_id}:\s*\n(?:(?!\n\S).*\n)*)"
    match = re.search(case_pattern, content, re.MULTILINE)
    
    if not match:
        logger.warning(f"Patcher: Could not find test case {test_case_id} in {file_path}")
        return False

    case_block = match.group(1)
    
    # 2. Within that block, find the step_key line
    # Matches "step_key: { ... }" or "step_key: \n    ..."
    # We target specifically the inline dictionary format used in Katana YAMLs
    step_pattern = rf"(\s+{step_key}:\s*)\{{.*\}}"
    
    # Format new_locator properly for YAML inline dict
    # e.g., { role: 'button', name: 'Got it' }
    items = []
    for k, v in new_locator.items():
        if k == 'description': continue # Skip AI-only descriptions
        items.append(f"{k}: '{v}'")
    new_locator_str = f"{{ {', '.join(items)} }}"
    
    if re.search(step_pattern, case_block):
        # Found inline dict, replace it
        new_case_block = re.sub(step_pattern, rf"\1{new_locator_str}", case_block)
    else:
        # Check for empty dict or multi-line (though Katana mostly uses inline)
        empty_pattern = rf"(\s+{step_key}:\s*)\{{\s*\}}"
        if re.search(empty_pattern, case_block):
             new_case_block = re.sub(empty_pattern, rf"\1{new_locator_str}", case_block)
        else:
            logger.warning(f"Patcher: Could not find locator pattern for step {step_key} in case {test_case_id}")
            return False

    # 3. Replace the old block in the full content
    new_content = content.replace(case_block, new_case_block)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    logger.info(f"🚀 Self-Healing: Successfully patched {test_case_id} -> {step_key} in {os.path.basename(file_path)}")
    return True

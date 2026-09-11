"""Migrated from Apifox case #5530131. Source folder: Subdomain."""
# Apifox Case ID: 5530131  (traceability only — not needed to run)
NAME = "After verifying that promoter has two subdomains, you can switch between them at will"
TAGS = ["p0", "subdomain", "suite:linda"]
PRIORITY = 0


CASE_ID = 5530131
ENV_NAME = "Release"

# --- step 1: 35a8e6ec-64ae-4978-ba8f-e4b614df64bf ---
# --- step 2: b3509af3-afbc-43a7-87ea-8531bfaeebc3 ---




from core.assertions import expect

def test_yuxiao_t2668_after_verifying_that_promoter_has_two_subdomains_you_can_switch_between_them_at_will(ctx):
    """Apifox case #5530131: YuXiao_T2668_After_verifying_that_promoter_has_two_subdomains_you_can_switch_bet"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 35a8e6ec-64ae-4978-ba8f-e4b614df64bf
    _resp1 = ctx.api.external.v_1129_2(body=None)
    # step 2: b3509af3-afbc-43a7-87ea-8531bfaeebc3
    _resp2 = ctx.api.external.v_1129(body=None)

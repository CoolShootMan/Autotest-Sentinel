Login token:
（原文为 `release_katana_web_auth_token_refresh` 的值，供开发登入复现；凭证不在此文件重复保留，见 Jira 票面）

URL:
https://release.pear.us/autotestshop/post/auto-test-post-setting-t1742

## Environment

- Release: https://release.pear.us (API `release.katana-api.1m.app`)
- Original post (shop owner): `0916aead-3496-4773-90fb-1f04adcdaba0` - /autotestshop/post/auto-test-post-setting-t1742
- Resale post (co-seller): `7af9d810-1ed7-429c-a532-ea2f760e49e6`, its `parentPostId` is `0916aead-3496-4773-90fb-1f04adcdaba0`
- Feature ticket: KAT-12117 (Operation: allow every post to customize the contact email)

## Preconditions

- The original post has "Use a different contact email" switched **ON** with a custom email configured (observed value at test time: `kat12117-owner@1m.app`).
- A co-seller account is permitted to resell that post.

### Reproduce Step:

1. The partner created a post and set "Use a different contact email".
2. As the co-seller, open the same post, click "Add to shop", then click Save in the "This post has been added to your shop." dialog.
3. Open the resale post's Post settings and check the "Use a different contact email" switch.
4. Open the post page and check the contact email rendered at the bottom.

<!--MEDIA-->

## Actual Result

The resale post is created with `contactEmail` empty:

- `GET /posts/curator/preview/7af9d810-1ed7-429c-a532-ea2f760e49e6` returns `contactEmail: null`, while its `parentPostId` is `0916aead-3496-4773-90fb-1f04adcdaba0` - so it really is a child of the configured post.
- In the resale post's Post settings, the "Use a different contact email" switch is OFF and the gear icon is absent.
- The contact email shown for that post falls back to the customer support email from Business settings (`test@pear.us`) instead of the address the original post configured.
- Related observation: while a co-seller is logged in, the contact email rendered at the bottom of the post is the Business settings value, not the value configured on the post.

## Expected Result

The resale post of the co-seller should inherit the "Use a different contact email" setting from the original post: `contactEmail` equals the original post's value and the switch is ON, so the bottom of the post shows the inherited custom email.

## Root cause (analysis)

The co-sell / "Add to shop" API does not carry the original post's advanced settings over to the newly created resale post. The resale post is built from the settings snapshot taken at resale creation time, and that snapshot contains no value for this field, hence `contactEmail = null`. As a consequence, both the resale post's own Post settings and the resale-side rendering of the post fall back to the Business settings customer support email.

## Impact

- Every co-selling post created after this feature ships will not carry the contact email customisation, and the same is true for the resale-side view of the post.
- Because the fallback is the shop-level Business settings address, a customer who contacts the reseller reaches the shop support mailbox instead of the address the post owner configured, so the post owner may never receive the message.
- Worth checking whether other post-level advanced settings are likewise missing from the resale snapshot (same API path).

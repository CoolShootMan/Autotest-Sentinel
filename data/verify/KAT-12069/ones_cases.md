# ONES 用例清单 — https://ones.cn/project/#/testcase/team/T7u1zXum/plan/3XhGxsKq/library

- 库：Katana (``)
- 计划：`3XhGxsKq`
- 拉取时间：2026-09-18 11:57:19    用例数：12

## [T5735] Verify the footnote is visible to visitors as well as the owner, not only to the owner

- 模块：My Shop / Storefront / Edit Profile / Storefront    优先级：P1    类型：functional    uuid：`C2WVmVUe`
- 前置条件：A footnote is configured on the storefront.
- 说明：Confirms the configured footnote is displayed across viewer perspectives: the owner sees the content plus an edit control, while a logged-out visitor sees the same content without any edit control.

| # | 步骤 | 预期结果 |
|---|------|----------|
| 1 | As the owner, view the storefront bottom | The footnote content is shown together with an "Edit footer" CTA |
| 2 | As a logged-out visitor (private window), view the storefront bottom | The same footnote content is shown with no edit control |

## [T5734] Verify editing an existing footnote updates it everywhere and clearing all content removes the footer section

- 模块：My Shop / Storefront / Edit Profile / Storefront    优先级：P1    类型：functional    uuid：`5CRKg37w`
- 前置条件：A footnote is already configured on the storefront.
- 说明：Confirms existing footnote content is loaded for editing, updates propagate to the storefront across desktop and mobile, and saving an empty footer removes the footnote section entirely.

| # | 步骤 | 预期结果 |
|---|------|----------|
| 1 | Click "Edit footer" | The editor opens pre-filled with the existing footnote content |
| 2 | Modify the content (e.g. add a word) and click "Save" | Both desktop and mobile storefronts show the updated footnote |
| 3 | Open the editor again, clear all content, and click "Save" | Save succeeds and the footnote section is no longer rendered on the storefront |
| 4 | Reload the storefront | No footnote is shown and the owner bottom entry is back to "Add footer" |

## [T5733] Verify the footnote does not conflict with the cookie preferences / Powered by Pear block

- 模块：My Shop / Storefront / Edit Profile / Storefront    优先级：P0    类型：functional    uuid：`PMkmD88F`
- 前置条件：A footnote is configured on the storefront.
- 说明：Confirms the configured footnote and the default Powered by Pear / cookie preferences area coexist without overlap and are visually tasteful on desktop and mobile.

| # | 步骤 | 预期结果 |
|---|------|----------|
| 1 | View the storefront bottom on desktop | The footnote renders above the "POWERED BY Pear" and "Cookie preferences" area with a divider and tasteful spacing; there is no overlap or clipping |
| 2 | View the storefront bottom on mobile | Same correct, non-conflicting layout on mobile |
| 3 | Open the cookie preferences entry | The cookie preferences entry remains accessible and is not obscured by the footnote |

## [T5732] Verify the footnote always stays at the very bottom and is excluded from Rearrange section

- 模块：My Shop / Storefront / Edit Profile / Storefront    优先级：P0    类型：functional    uuid：`7TJjrvwm`
- 前置条件：A footnote is configured; the storefront has multiple sections/modules.
- 说明：Confirms the footnote is pinned to the bottom of the storefront, has a divider above it consistent with existing storefront dividers, and is not part of the Rearrange section list.

| # | 步骤 | 预期结果 |
|---|------|----------|
| 1 | Open "Rearrange section" on the storefront | The footnote is NOT listed among the rearrangeable sections |
| 2 | Reorder the available sections and save | Other sections change order while the footnote remains at the very bottom |
| 3 | Verify the divider above the footnote | A divider is shown above the footnote, consistent with existing storefront dividers |

## [T5731] Verify the footnote text color and font follow the Storefront Style settings

- 模块：My Shop / Storefront / Edit Profile / Storefront    优先级：P1    类型：functional    uuid：`DxtYysg3`
- 前置条件：A footnote is configured on the storefront.
- 说明：Confirms the footnote inherits its text color from style > color > text and its font from style > fonts, and cannot be overridden per footnote.

| # | 步骤 | 预期结果 |
|---|------|----------|
| 1 | Open Customize shop / Style and change the text color (style > color > text) | The footnote text color on the storefront updates accordingly |
| 2 | Change the font (style > fonts) | The footnote font updates accordingly |
| 3 | Re-open the footnote editor and check the available controls | The footnote still cannot override color, font size, or spacing in the RTE |

## [T5730] Verify the Insert link dialog requires link text and a URL and rejects an invalid URL

- 模块：My Shop / Storefront / Edit Profile / Storefront    优先级：P1    类型：functional    uuid：`3B1fnc1b`
- 前置条件：The footnote editor is open and the Insert link dialog is open.
- 说明：Confirms required-field validation in the Insert link dialog: the Add button stays disabled until link text and a URL are provided, and an invalid URL is rejected.

| # | 步骤 | 预期结果 |
|---|------|----------|
| 1 | Leave "Link text" and the URL empty and observe the "Add" button | "Add" is disabled until the required fields are provided |
| 2 | Enter link text but leave the URL empty | "Add" stays disabled or a validation message is shown |
| 3 | Enter an invalid URL (e.g. "abc" with no valid domain) and click "Add" | The invalid URL is rejected; the link is not inserted and an error is shown |
| 4 | Enter a valid URL and click "Add" | The link is inserted successfully |

## [T5729] Verify inserting an external link in the footnote renders it underlined and not blue

- 模块：My Shop / Storefront / Edit Profile / Storefront    优先级：P1    类型：functional    uuid：`6XMdxcTk`
- 前置条件：The footnote editor is open with text available to link.
- 说明：Confirms the Insert link dialog defaults to "External link" and that a link inserted into the footnote is displayed underlined but never blue on the storefront.

| # | 步骤 | 预期结果 |
|---|------|----------|
| 1 | Select text and click the link icon in the RTE toolbar | The "Insert link" dialog opens |
| 2 | Check the default value of the "Action" dropdown | "External link" is selected by default |
| 3 | Enter link text and a URL (e.g. https://example.com) and click "Add" | The link is inserted into the footnote text |
| 4 | Save and view the footnote on the storefront | The link is displayed with an underline but is not blue |

## [T5728] Verify the footnote RTE editor exposes the required quick actions with centered default alignment and no style-override controls

- 模块：My Shop / Storefront / Edit Profile / Storefront    优先级：P0    类型：functional    uuid：`84u4Gooi`
- 前置条件：The footnote editor is open.
- 说明：Confirms the footnote RTE editor supports undo, redo, bold, underline, link and alignment (centered by default), and does not offer color, font size or spacing controls.

| # | 步骤 | 预期结果 |
|---|------|----------|
| 1 | Inspect the RTE toolbar | The toolbar shows undo, redo, bold, underline, link and alignment controls |
| 2 | Type sample text and verify the default alignment | Text is centered by default |
| 3 | Apply bold to one word and underline to another word | Bold and underline are applied and visible in the editor |
| 4 | Look for color, font size, or spacing controls | No color, font size, or spacing controls are available in the RTE |

## [T5727] Verify "Insert copyright template" auto-fills the default copyright template text and centers it

- 模块：My Shop / Storefront / Edit Profile / Storefront    优先级：P1    类型：functional    uuid：`VeWxrSsG`
- 前置条件：The footnote editor is open with empty content.
- 说明：Confirms that clicking "Insert copyright template" auto-fills the default template copy (privacy/terms links plus a copyright line) centered by default. Per the design this capability is low priority and may land in a later cycle.

| # | 步骤 | 预期结果 |
|---|------|----------|
| 1 | Click the "Insert copyright template" link in the footnote editor | The template copy is auto-filled into the editor: "(c) 2026 Your legal entity name. All rights reserved." |
| 2 | Check the alignment of the inserted template | The inserted template is centered by default |
| 3 | Click "Save" and view the storefront | The template copy renders centered at the bottom of the storefront |

## [T5726] Verify the footnote change takes effect on the storefront immediately after saving, without a refresh

- 模块：My Shop / Storefront / Edit Profile / Storefront    优先级：P1    类型：functional    uuid：`4WBTxGGR`
- 前置条件：A footnote is configured on the storefront and the partner is viewing their own storefront.
- 说明：Confirms that after the partner edits and saves the footnote, the storefront bottom reflects the updated content immediately, without the user having to reload the page.

| # | 步骤 | 预期结果 |
|---|------|----------|
| 1 | Open the footnote editor, modify the existing footnote text (including applying bold to part of it), and click Save | The editor closes with a success confirmation and the change is saved |
| 2 | Without refreshing the storefront page, scroll to the bottom of the storefront | The storefront bottom immediately shows the updated footnote content, including the bold formatting, with no page refresh required |
| 3 | Reload the storefront page and re-check the footnote | The updated footnote persists at the bottom of the storefront |

## [T5725] Verify the footnote section is hidden when no footnote is configured and only an "Add footer" entry is shown to the owner

- 模块：My Shop / Storefront / Edit Profile / Storefront    优先级：P0    类型：functional    uuid：`V7byhv7p`
- 前置条件：Partner owns a published storefront; the footnote is empty / not configured.
- 说明：Confirms that when no footnote content is configured, no footnote section is rendered for visitors on the storefront, and the owner only sees an "Add footer" call to action.

| # | 步骤 | 预期结果 |
|---|------|----------|
| 1 | As a visitor (private window), open the storefront and scroll to the very bottom | No footnote section is rendered; the page ends with the default Powered by / cookie area |
| 2 | As the owner, open the storefront and check the bottom | An "Add footer" CTA is displayed instead of an "Edit footer" CTA |
| 3 | Click "Add footer" and close the editor (X) without saving any content | The editor closes; the storefront still shows no footnote section |

## [T5724] Verify a partner can add a storefront footnote via the RTE editor and it renders at the bottom for visitors on desktop and mobile

- 模块：My Shop / Storefront / Edit Profile / Storefront    优先级：P0    类型：functional    uuid：`WGbefTCA`
- 前置条件：Partner is logged in and owns a published storefront; no footnote is configured yet.
- 说明：End-to-end happy path: a partner with no footnote configured opens the footnote editor from the storefront, enters content with the RTE editor, saves, and the footnote renders at the very bottom of the storefront with a divider above it for both the owner and visitors on desktop and mobile.

| # | 步骤 | 预期结果 |
|---|------|----------|
| 1 | Open the partner's storefront (Shop view) and scroll to the bottom | The bottom shows an "Add footer" CTA and no footnote section is rendered |
| 2 | Click "Add footer" | The "Storefront footer" editor opens with the RTE toolbar visible and the content area empty |
| 3 | Enter footnote text in the RTE editor (e.g. "Contact Us \| Privacy Policy \| Terms & Conditions") | The typed content appears in the editor |
| 4 | Click "Save" | The editor closes with a success confirmation; the storefront now shows the footnote content at the bottom with a divider above it |
| 5 | Reload the storefront page and re-check the footnote position | The footnote persists and stays at the very bottom of the storefront |
| 6 | Open the same storefront URL in a private window as a visitor and scroll to the bottom | Visitors also see the footnote; no edit control is shown to visitors |
| 7 | Repeat the check on a mobile viewport | The footnote renders correctly on mobile as well |

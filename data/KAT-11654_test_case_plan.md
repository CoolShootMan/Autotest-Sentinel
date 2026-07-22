# KAT-11654 Test Case Plan
## Collabs: Revamp Post Invite Acceptance Experience

**Ticket**: KAT-11654  
**Module**: My Shop → Collabs (`3pfH7pm8`)  
**QA Owner**: Yuxiao Zhu  
**Date**: 2026-07-22  
**ONES Plan**: `JxAZP9Xw` — [Open in ONES](https://ones.cn/project/#/testcase/team/T7u1zXum/plan/JxAZP9Xw/library)  
**Jira**: [KAT-11654](https://pearshop.atlassian.net/browse/KAT-11654) (Test Case Link for QA field backfilled)  
**Status**: ✅ 26 cases (8 modify + 18 new), all updated in ONES with verified steps, linked to plan, Jira backfilled. B13 merged into B12.  

---

## Overview

KAT-11654 revamps the post-invite-acceptance experience for Collabs. The core problem: co-sellers were redirected to the Explore page after accepting an invitation, causing confusion. The new flow redirects them to their own shop with post preference selection and section choice.

### Scope
1. **Invite acceptance flow** (4 user scenarios) — redirect changes, post preferences
2. **Add Shoppable posts** (3 entry points) — new CTA
3. **Post-based flow** — partner manually adds posts to co-seller's shop (NOT an invite flow)
4. **Two invitation types** — public (official link) vs private (partner-generated link)

### Terminology
- **co-seller**: the user who accepts the invitation (was called "promoter/curator" in old cases)
- **partner**: the user who sends the invitation (was called "curator/merchant" in old cases)

---

## Part A: Cases to MODIFY (existing cases needing updates)

### A1. `V8of7NTm` — "Invite guest/promoter to register and enter the Explore page"
- **Status**: ✅ Updated in ONES (title + 7 steps)
- **Current**: New user registers via invite link → lands on Explore page
- **New**: New user registers via invite link → creates shop (name + URL) → lands on own Storefront
- **Priority**: P0
- **Changes**: Update title to remove "Explore page", update steps to include shop name creation and redirect to own shop
- **Scenario**: New co-seller (new user, full onboarding)

### A2. `8TQ1JwU5` — "Verifying that a promoter who has established contact with the merchant uses the invitation link again will directly redirect to explore"
- **Status**: ✅ Updated in ONES (title + 6 steps)
- **Current**: Already-connected co-seller clicks invite link → redirect to Explore
- **New**: Already-connected co-seller clicks invite link → redirect to My Shop with Toast notification showing inviting shop name
- **Priority**: P0
- **Changes**: Update title and steps — redirect target changes from Explore to My Shop; add Toast notification verification
- **Scenario**: Logged in + Already a co-seller

### A3. `4t935FGh` — "After verifying that the Promoter/Curator accepts the invitation, it will be displayed in the My promoters/My Curator list"
- **Status**: ✅ Updated in ONES (title + 9 steps)
- **Current**: Basic acceptance → appears in list
- **New**: Acceptance now includes post preference selection (auto-add vs manual) and section choice → redirect to Added section
- **Priority**: P0
- **Changes**: Add steps for post preference selection, section selection, and redirect to Added section after acceptance
- **Scenario**: Logged in + Not a co-seller (existing user)

### A4. `BxcrNWgC` — "After verifying that the logged in Promoter accepts the invitation, the Curator appears in the Partner curators list"
- **Status**: ✅ Updated in ONES (title + 8 steps)
- **Current**: Logged-in user accepts → appears in partner's list
- **New**: Logged-in user accepts → sees post preference screen (auto-add toggle + section selection) → redirect to Added section
- **Priority**: P0
- **Changes**: Add post preference and section selection steps to the acceptance flow
- **Scenario**: Logged in + Not a co-seller

### A5. `QQZTGHFf` — "For the first time, an unlogged Consumer logs into Katana via Merchant link and completes the resale flow"
- **Status**: ✅ Updated in ONES (title + 8 steps)
- **Current**: Unlogged consumer → login via merchant link → complete resale
- **New**: Unlogged consumer → login via invite link → email verification → create shop (name + URL) → accept invite → post preferences → redirect to own shop
- **Priority**: P0
- **Changes**: Major rewrite — add shop creation step, post preference selection, and redirect to own shop instead of resale flow
- **Scenario**: Logged out + Not a co-seller (existing user) / New user

### A6. `GKX35khK` — "Verify the right merchant invitation link could invite the promoter successfully"
- **Status**: ✅ Updated in ONES (title + 8 steps)
- **Current**: Basic invite link → successful invitation
- **New**: Invite link → landing page with benefits → accept → post preferences → redirect to Added section
- **Priority**: P0
- **Changes**: Add post preference selection and redirect verification steps
- **Scenario**: General invitation acceptance

### A7. `6mzmgWYT` — "Verify the function of generating invitation link"
- **Status**: ✅ Updated in ONES (title + 8 steps)
- **Current**: Generate invitation link
- **New**: Now includes private invitation link generation (partner generates for specific co-seller)
- **Priority**: P0
- **Changes**: Add steps for private invitation link generation and verify difference from public link
- **Scenario**: Partner generates invite link

### A8. `T4101` / `BPWMu4zC` — "Verify new shop profile card on collabs > partnered shops page"
- **Module**: My Shop → Collabs → My Curators (`WpmDzbEo`)
- **Priority**: P0
- **Assignee**: Demi Hu (`K2uAHwKp`) — restored to original owner
- **Status**: ✅ Restored + updated in ONES
- **Changes**: 
  - Original title restored: `Verify new shop profile card on collabs > partnered shops page`
  - Original precondition restored (KAT-9128 No.5)
  - Original assignee restored
  - Kept the original profile-card verification steps
  - **Appended** 4 new steps covering the invite-flow mirror of the post preference settings (auto-add toggle + storefront section selection)
- **Scenario**: Partnered shop profile card + invite acceptance flow post-preference synchronization

---

## Part B: Cases to CREATE NEW

> **Status**: ✅ All 18 cases created in ONES with steps and priorities set (B13 merged into B12). New case UUIDs recorded in `data/ones_create_results.json`. All steps verified via GraphQL `testcaseCaseSteps` query.

### Category 1: Invite Acceptance — New Scenarios

#### B1. Verify "Save as draft" defers invitation acceptance
- **Priority**: P1
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Logged in + Not a co-seller
- **Precondition**: User is logged in, has received a Collabs invitation link
- **Steps**:
  1. Open the Collabs invitation link while logged in
  2. Verify the invite landing page shows "You're invited!" with partner shop name and benefits
  3. Click "Save as draft"
  4. Verify the invitation is saved and user is not yet a co-seller
  5. Verify user can return to accept the invitation later
- **Expect**: Invitation is saved as draft, no co-seller relationship established yet

#### B2. Verify "Browse shop first" allows viewing partner's shop before accepting
- **Priority**: P1
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Logged in + Not a co-seller
- **Precondition**: User is logged in, has received a Collabs invitation link
- **Steps**:
  1. Open the Collabs invitation link while logged in
  2. Verify the invite landing page shows "Browse shop first" button
  3. Click "Browse shop first"
  4. Verify user is redirected to the partner's shop page
  5. Verify user can return to the invitation page to accept
- **Expect**: User can preview partner's shop without accepting the invitation

#### B3. Verify new user with no existing sections defaults to "Add to New Section"
- **Priority**: P1
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: New co-seller (new user, full onboarding)
- **Precondition**: New user has just created their shop and has no existing storefront sections
- **Steps**:
  1. Complete the new user signup via invite link (email → verification → shop creation)
  2. On the post preference screen, verify "Add to New Section" is selected by default
  3. Verify the section dropdown only shows "Add to New Section" option (no existing sections)
  4. Complete the acceptance flow
  5. Verify the post is added to a new section, not to "My Content"
- **Expect**: New users without sections get posts in a new section, preventing posts from being lost in My Content

#### B4. Verify already-co-seller redirect shows Toast notification with inviting shop name
- **Priority**: P0
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Logged in + Already a co-seller
- **Precondition**: User is logged in and already a co-seller of the partner
- **Steps**:
  1. Open the Collabs invitation link from a partner the user is already connected to
  2. Verify the user is redirected to My Shop (not the invite landing page)
  3. Verify a Toast notification appears showing the inviting partner's shop name
  4. Verify the invite acceptance flow is NOT shown
  5. Verify user can browse Partner Shoppable Posts from My Shop
- **Expect**: Already-connected co-seller is redirected to My Shop with a Toast, no duplicate acceptance flow

---

### Category 2: Post Preferences & Section Selection

#### B5. Verify auto-add posts toggle is enabled by default during invite acceptance
- **Priority**: P0
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: All acceptance scenarios
- **Precondition**: User is on the post preference screen during invite acceptance
- **Steps**:
  1. Reach the post preference screen after accepting the invitation
  2. Verify "Auto-add posts from this partner" toggle is ON by default
  3. Verify the description text "Never miss a sale. You can change this anytime." is displayed
  4. Verify "I'll choose which posts to add" option is also available
  5. Toggle auto-add OFF and verify the description changes to "Review each post before adding it."
- **Expect**: Auto-add is enabled by default, user can toggle it off

#### B6. Verify "Choose where posts appear on storefront" section selection
- **Priority**: P0
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: During invite acceptance and in Collabs settings
- **Precondition**: User has existing storefront sections
- **Steps**:
  1. On the post preference screen, verify "Choose where posts appear on your storefront." text is displayed
  2. Verify the section dropdown shows existing sections
  3. Verify "Add to new section" option is available
  4. Select an existing section
  5. Complete the acceptance flow
  6. Verify posts are added to the selected section
  7. Change the section selection in Collabs settings later and verify it updates
- **Expect**: User can choose which storefront section receives auto-added posts

#### B7. Verify auto-add toggle setting syncs with partner's Collabs settings
- **Priority**: P1
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Post-acceptance settings management
- **Precondition**: Co-seller has accepted invitation with auto-add enabled
- **Steps**:
  1. Navigate to My Shop → Collabs → My Co-sellers
  2. Find the partner in the list
  3. Verify the "Allow this partner to add new posts to my shop automatically" toggle is ON
  4. Toggle it OFF
  5. Verify the change syncs to the partner's Collabs settings
  6. Toggle it back ON and verify sync again
- **Expect**: Auto-add setting changes are bidirectionally synced between co-seller and partner

#### B8. Verify redirect to Added section after posts are applied
- **Priority**: P0
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Post-acceptance redirect
- **Precondition**: User has just completed the invite acceptance flow with post preferences selected
- **Steps**:
  1. Complete the invite acceptance flow with auto-add enabled and a section selected
  2. Verify the user is redirected to the Added section on their storefront
  3. Verify the added posts are visible in the selected section
  4. Verify the user is NOT redirected to the Explore page
- **Expect**: User lands on their own storefront's Added section, not Explore

---

### Category 3: Add Shoppable Posts (3 Entry Points)

#### B9. Verify Add Shoppable posts via Add menu entry point
- **Priority**: P0
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Partner adds shoppable posts from Add menu
- **Precondition**: User is a co-seller with at least one connected partner
- **Steps**:
  1. Navigate to My Shop
  2. Click the "Add" button in the top menu
  3. Verify "Add Shoppable posts" option appears in the dropdown
  4. Click "Add Shoppable posts"
  5. Verify the Partners' Shoppable posts page opens
  6. Verify posts from connected partners are displayed
- **Expect**: Add menu provides an entry point to browse and add partner shoppable posts

#### B10. Verify Add Shoppable posts via Storefront section entry point
- **Priority**: P0
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Partner adds shoppable posts from Storefront
- **Precondition**: User is on their Storefront page
- **Steps**:
  1. Navigate to My Shop → Storefront
  2. Verify an "Add Shoppable posts" CTA is visible in a storefront section
  3. Click the "Add Shoppable posts" CTA
  4. Verify the Partners' Shoppable posts page opens
  5. Verify posts from connected partners are displayed
- **Expect**: Storefront section provides an entry point to browse and add partner shoppable posts

#### B11. Verify Add Shoppable posts via "Start selling" after invite acceptance
- **Priority**: P0
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Post-invite-acceptance entry point
- **Precondition**: User has just completed the invite acceptance flow
- **Steps**:
  1. Complete the invite acceptance flow
  2. Verify the success screen shows "Start selling" button
  3. Verify the success message "You're now a co-seller for [Shop name]" is displayed
  4. Click "Start selling"
  5. Verify the Partners' Shoppable posts page opens
  6. Verify posts from the inviting partner are displayed
- **Expect**: Post-acceptance "Start selling" button leads to Partners' Shoppable posts

---

### Category 4: Partners' Shoppable Posts — Browse & Add

#### B12. Verify Partners' Shoppable posts list with filter, sort, and sort semantics
- **Priority**: P1
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Browsing partner posts + sort behavior verification
- **Precondition**: Multiple partner shops with posts added at different times
- **Steps** (merged B12 + B13, 10 steps):
  1. Navigate to Partners' Shoppable posts (via any entry point)
  2. Verify the page title "Partners' Shoppable posts" is displayed
  3. Verify a shop filter is available
  4. Verify a sort dropdown is available with options: Newest, Recently Added, Most viewed, Best selling, Top commission
  5. Verify default sort is "Newest" in non-filtered state
  6. Switch sort to "Recently Added" and verify the list updates
  7. Use the shop filter to filter by a specific partner shop
  8. Sort by "Newest" — verify posts are ordered by latest posts from all partner shops
  9. Sort by "Recently Added" — verify posts are ordered by new partners/shops added to the shop
  10. Verify the two sorts produce different orderings when applicable
- **Expect**: Users can filter by shop, sort by multiple criteria, and "Newest" vs "Recently Added" have distinct semantics

#### ~~B13. Verify "Newest" vs "Recently Added" sort semantics~~ (MERGED into B12)
- **UUID**: `UNXyWFMC` — removed from plan `JxAZP9Xw` (case still exists in library but not linked to plan)

#### B14. Verify adding individual posts to shop from Partners' Shoppable posts
- **Priority**: P0
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Adding posts manually
- **Precondition**: User is on the Partners' Shoppable posts page
- **Steps**:
  1. Browse the Partners' Shoppable posts list
  2. Click "Add to shop" on a specific post
  3. Verify a section selection dialog appears: "Choose where you'd like to feature on your storefront."
  4. Select a section (or "Add to a new section")
  5. Click "Apply"
  6. Verify "Added to your shop." confirmation appears
  7. Navigate to the selected section on storefront and verify the post is there
- **Expect**: User can manually add individual partner posts to a chosen storefront section

#### B15. Verify "You're already a co-seller for this partner" state on Partners' Shoppable posts
- **Priority**: P1
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Already connected partner
- **Precondition**: User is already a co-seller of the partner whose posts they're browsing
- **Steps**:
  1. Open Partners' Shoppable posts
  2. Filter by a partner the user is already connected to
  3. Verify "You're already a co-seller for this partner." text is displayed
  4. Verify "Browse and add posts to resell." subtext is shown
  5. Verify posts are available to add to shop
- **Expect**: Already-connected partners show appropriate messaging but still allow adding posts

---

### Category 5: Post-Based Flow (Partner Adds Posts to Co-seller's Shop)

#### B16. Verify partner manually adds post to co-seller's storefront
- **Priority**: P0
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Post-based flow — partner action
- **Precondition**: Partner has a co-seller with auto-add enabled
- **Steps**:
  1. As the partner, navigate to a post's Co-selling tab
  2. Select "Add to co-seller's shop" for a connected co-seller
  3. Verify the post is added to the co-seller's storefront
  4. Verify the post appears in the section configured by the co-seller's settings
- **Expect**: Partner can manually push posts to a co-seller's storefront

#### B17. Verify co-seller receives notification when partner adds posts
- **Priority**: P1
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Post-based flow — co-seller notification
- **Precondition**: Partner has just added a post to co-seller's shop
- **Steps**:
  1. As the co-seller, navigate to My Shop
  2. Verify a notification/alert appears: "1 new post added to your shop" (or "2 new posts added to your shop" for multiple)
  3. Click the notification
  4. Verify user is taken to the Added section where the new post(s) are located
- **Expect**: Co-seller is notified when a partner adds posts to their shop

#### B18. Verify post-based addition respects auto-add toggle setting
- **Priority**: P1
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Post-based flow — auto-add interaction
- **Precondition**: Co-seller has auto-add toggle OFF for a partner
- **Steps**:
  1. As the co-seller, turn OFF auto-add for a specific partner in Collabs settings
  2. As the partner, attempt to add a post to the co-seller's shop
  3. Verify the post is NOT automatically added to the co-seller's storefront
  4. As the co-seller, check Partners' Shoppable posts — verify the post is available to add manually
- **Expect**: When auto-add is OFF, partner-pushed posts require manual approval from co-seller

---

### Category 6: Invitation Types

#### B19. Verify public invitation link (official) vs private invitation link (partner-generated)
- **Priority**: P0
- **Module**: My Co-sellers (`K9GYKa95`)
- **Scenario**: Two invitation types
- **Precondition**: Partner has both public and private invitation links
- **Steps**:
  1. As the partner, navigate to My Shop → Collabs → My Co-sellers
  2. Verify the default/public invitation link is available (official invite link)
  3. Verify the partner can generate a private invitation link for a specific co-seller
  4. Open the public invitation link as a new user — verify standard invite landing page
  5. Open the private invitation link as the target user — verify standard invite landing page
  6. Verify both link types lead to the same acceptance flow with post preferences
- **Expect**: Both public and private invitation links work, private links are partner-generated for specific users

---

## Part C: Resolved — Existing Case Found

- **`T4101`**: "Verify new shop profile card on collabs > partnered shops page" (My Shop → Collabs → My Curators)
- **Action**: Modify title and add steps to cover the post preference settings (auto-add toggle + section selection) now shown on the partnered shop profile card.
- **Note**: The original Collabs settings location for these controls is retained, so this case only needs content updates, not removal.

---

## Summary

| Category | Modify | New | Total |
|----------|--------|-----|-------|
| Invite Acceptance (4 scenarios) | 6 | 4 | 10 |
| Post Preferences & Section Selection | 1 | 4 | 5 |
| Add Shoppable Posts (3 entry points) | 0 | 3 | 3 |
| Partners' Shoppable Posts Browse & Add | 0 | 3 | 3 |
| Post-Based Flow | 0 | 3 | 3 |
| Invitation Types | 1 | 1 | 2 |
| **Total** | **8** | **18** | **26** |

### Priority Breakdown
- **P0**: 17 cases (main flows + critical new features)
- **P1**: 9 cases (edge cases + secondary features, B13 merged into B12)

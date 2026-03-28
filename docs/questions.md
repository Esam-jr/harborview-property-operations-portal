# Questions & Clarifications

Record of all questions raised during the process of understanding the business logic in the Prompt. 


### Inheritance and Overlap of User Roles

**Question:** The prompt includes staff roles like "Administrator", "Property Manager", "Accounting Clerk", and "Maintenance/Dispatcher", but did not completely clarify the differences or boundaries in permission scope for modifying specific data.

**My Understanding:** Staff should have strict domain segregation based on their specific roles to prevent accidents, but Administrators should have overarching access to all system states. 

**Solution:** Implemented role-based route and object-level authorization gates (tracked via `UserRole` enum and `api/deps/`). Property Managers manage listings, Dispatchers handle service orders, and Clerks manage billing, while Residents can only view their own data.

### Offline Mode Data Synchronization

**Question:** The prompt calls for "an optional installable offline mode" but did not specify how data write conflicts (e.g. a resident submitting a service order while offline) or deferred writes are handled when network is lost.

**My Understanding:** Implementing full multi-user offline conflict resolution is overly heavy; an optimistic queuing mechanism for resident actions or staff status updates when the network is lost is sufficient.

**Solution:** Leveraged Vue.js and PWA Service Workers (`frontend/src/services/pwaService.js`) that cache static assets locally and explicitly monitor `online`/`offline` navigator states to gracefully manage the application experience when connections drop.

### Refund Requests and Ledger Management

**Question:** The prompt states residents can "request refunds as credits," but does not explicitly mention if credits are automatically applied on the active ledger or if they require manual Accounting Clerk approval first.

**My Understanding:** Automatically altering ledger states introduces reconciliation risks. Credits should be modeled as state transitions that are reviewed and approved by an Accounting Clerk before applying to an overarching balance.

**Solution:** Centralized billing logic with specific Enum states (`pending`, `paid`, `overdue`, `refunded` in `models/enums.py`), creating a workflow where a resident's refund request flags the specific billing record, allowing the Clerk to approve it manually.

### 10% Rollout Configuration Toggle Criteria

**Question:** The prompt requires a "controlled rollout toggle so a new configuration can be shown to 10% of staff accounts first," but does not explicitly specify how the 10% calculation is distributed or maintained across sessions.

**My Understanding:** Randomizing per-session causes UI flickering and confusion for the same staff member across refreshes. The 10% bucket must be deterministic and stable for the lifetime of that configuration.

**Solution:** Built a deterministic mechanism (using a hash of the staff user's ID against the configuration version) to ensure consistent assignment to the 10% group for a given homepage configuration rollout.

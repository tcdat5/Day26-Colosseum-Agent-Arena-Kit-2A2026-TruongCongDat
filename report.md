# COLOSSEUM · Báo cáo vận hành theo từng bước

Ngày: 2026-08-29
Phạm vi: chạy đúng quy trình trong README.md/RULES.md trên trạng thái repo hiện tại, **không sửa
code bài tập** (agent/ deck/ eval/ giữ nguyên như đang dở dang). Mục tiêu là xác nhận repo chạy
được tới đâu và liệt kê chính xác phần còn thiếu.

---

## Bước 1 — `make install`

```
uv không có -> fallback sang .venv/bin/python -m venv
pip install pytest
```
✅ Thành công. `.venv/` đã sẵn, không cần API key (đúng như README §2 nói).

## Bước 2 — `make doctor`

```
G-KEY: PASS (100 files scanned, 0 violations)
world df8c55dabb35 - 176 pages
referee: 17 classes, local_only=True
ready to spar.
```
✅ World corpus đã có sẵn ở `kit/world/df8c55dabb35/` (không phải tải lại từ Releases).
`validate_deck.py` chạy kèm, 0 lỗi FAIL, 5 WARN (xem Bước 4).

## Bước 3 — Spar với cả 3 bot (`--as all`, tức cả Attack + Defend + Prosecute)

| Bot | Kết quả | HP cuối | Ghi chú |
|---|---|---|---|
| **rookie** (EASY) | 🟢 THẮNG | you 64 — 21 rookie | Đúng như README: thua Rookie nghĩa là có bug — ở đây không thua. |
| **operator** (MEDIUM) | 🟢 THẮNG áp đảo | you 82 — 0 operator | Deck xuyên thủng operator hoàn toàn ở R9. |
| **adversary** (HARD) | 🔴 THUA | you 0 — 78 adversary | HP tụt dần mỗi round (`took` 6–21/round), không gỡ lại được. |

**Điểm chung cả 3 trận — phần công tố (Task 2) đang bỏ trống hoàn toàn:**
```
MISSED — fabricated_citation  x5-6  family B  worth 8 mỗi lần — sát thương miễn phí bị bỏ qua
MISSED — protocol_misuse      x4-10 family A  worth 6 mỗi lần — sát thương miễn phí bị bỏ qua
```
Đây khớp với việc `eval/prosecute.py` hiện chỉ cài 1/17 lớp lỗi (xem Bước 5) — công tố không hề
đụng tới `fabricated_citation` hay `protocol_misuse` dù bằng chứng có sẵn trong trace của cả 3 bot.

## Bước 4 — `make test` (bộ test công khai / conformance check)

```
4 failed, 4605 passed, 4 skipped
```
4 test fail đều nằm trong `tests/test_isolation.py`, và đều vì lý do **môi trường, không phải bug
của bạn**: `sandbox-exec` là công cụ macOS-only, máy Linux này không có, nên các test tự chủ động
`pytest.fail(...)` với thông điệp "sandbox-exec is NOT AVAILABLE ... failing loudly instead of
skipping" — đây là hành vi được thiết kế có chủ đích trong kit (đúng CONTRACTS.md 12.2.4), không
phải lỗi ở `agent/`/`deck/`/`eval/`. **Có tests/test_gateway.py tự viết (3 test, chưa được commit)
đều PASS**, kiểm tra 3 nhánh: deny cross-learner write theo `ctx.act`, deny route giấu trong body
thay vì header, và rewrite catalog-trap fields — cả ba khớp với code hiện tại trong `gateway.py`.

## Bước 5 — `make validate`

```
PASS: 0 failing check(s), 5 warning(s)
```
Deck 14 lá hợp lệ về mặt cấu trúc (10 attack + 4 blank, đủ layer-mix, đủ lớp lỗi phân biệt). 5 WARN
đều là loại "không tự động xác nhận được, cần bạn tự soát tay":
- `R8-lethality-band`: hệ mutation thật nằm ở repo giảng viên, script này không tự chạy được một
  trận thật để đo lethality — phải tự soát bằng `spar.py` (đã làm ở Bước 3: thắng rookie ✓, held-nhưng-thua
  adversary — cần xem lại các lá chưa "held" được).
- `R8-held-in-principle` x4 (`atk_03`, `atk_04`, `atk_05`, `atk_09`): 4 lá dùng `defense_event` không
  đúng hình dạng `gateway.denied` mà proxy kiểm tra — không tự xác nhận được "held in principle",
  cần review thủ công.

## Bước 6 — Trạng thái implementation hiện tại (chỉ đọc, không sửa)

| File | Trạng thái | Còn thiếu |
|---|---|---|
| `agent/gateway.py` | **Đã sửa, chưa commit** (`git diff` +72/−39 dòng) | 3/4 job có code thật: ROUTE (route-in-body bị deny, replica route qua `strategy.pick_replica`), AUTHORIZE (cross-learner write bị deny theo `ctx.act`+scope), BUDGET (catalog-trap bị rewrite về cheap mask). **JOB 2 — ADMIT vẫn là placeholder**: chỉ còn lại comment mô tả việc cần làm, không có dòng code nào thật sự deny một call đã biết chắc sẽ hỏng (lease hết hạn, write thiếu `If-Match`, call đã 409 trước đó). *(Sửa lại so với báo cáo lần trước — lần đầu tôi ghi nhầm "không còn TODO nào".)* |
| `agent/strategy.py` | Có nội dung đầy đủ (476 dòng), được `gateway.py` import và gọi (`cheap_mask`, `is_catalog_trap`, `pick_replica`, `successor_of`) | Chưa audit sâu — nằm ngoài phạm vi review lần này (bạn chọn "không sửa code"). |
| `agent/guardrails.py` | 1/4 phần thật (`check_grounding`, `abstention_policy`); **3 stub còn nguyên**: `refuse_injected_instructions` (luôn `suspicious=False`), `redact` (luôn trả nguyên văn, `hits=()`), `verify_arithmetic` (luôn `checked=False`) | Đây là lỗ hổng sống duy nhất cho `guardrail_breach` (weight 8) theo chính `agent/README.md`. |
| `eval/prosecute.py` | **1/17 lớp lỗi được cài** (`enforcement_failure`, weight 10) — 16 hook còn lại (`_hook_stale_read`, `_hook_fabricated_citation`, `_hook_protocol_misuse`, ...) đều là stub trả `[]` | Tự báo cáo trong code: `precision=1.000, recall=0.059 — expected and correct` cho starter. Đây chính là lý do cả 3 trận spar ở Bước 3 đều "MISSED" `fabricated_citation` và `protocol_misuse`. |
| `deck/deck.json`, `deck/lineup.json` | Hợp lệ (`make validate` PASS) | 4 lá cần soát tay theo WARN ở Bước 5. |
| `tests/test_gateway.py` | File mới, chưa add vào git, 3 test PASS | Chưa `git add`; do bạn quyết định có giữ hay không. |

## Bước 7 — Chưa chạy

- `make ui` — cần trình duyệt để mở `spar.html`/`projector.html`, không chạy được trong phiên
  không-GUI này. Bỏ qua theo yêu cầu chỉ vận hành các bước dòng lệnh.
- `make submit TEAM=...` — **không chạy**, vì đây là hành động đóng gói/khoá bài nộp
  (`agent/`+`deck/` sẽ bị lock), không nên tự ý thực hiện. Cần bạn xác nhận `TEAM=<tên đội>` và có
  thật sự muốn seal bundle lúc này không.
- `make qualify` — README nói rõ lệnh này đã bị retired, không cần chạy.

---

## Bước 8 — Soát lại vòng 2: checklist việc cần làm (theo RULES.md/README.md)

Xếp theo mức ưu tiên / ROI, không sửa gì — chỉ liệt kê để bạn quyết định.

### 🔴 Cao — ảnh hưởng điểm trực tiếp, dễ đo bằng spar

1. **`agent/guardrails.py` — 3 stub còn nguyên** (`scan_for_injected_instructions`,
   `redact`, `verify_arithmetic`). Đây là tuyến phòng thủ SỐNG duy nhất cho
   `guardrail_breach` (8), `privacy_leak` (8), `unsupported_precision` (4) — khớp với
   việc thua adversary 0–78 ở Bước 3 (adversary "bốn lớp kiểm tra identity... kỷ luật"
   theo README §3, tức nó sẽ khai thác đúng những lỗ này).
2. **`agent/gateway.py` JOB 2 — ADMIT chưa có code** (xem sửa ở Bước 6). Đây là job
   duy nhất trong 4 job còn là placeholder thuần comment.
3. **`eval/prosecute.py` — 16/17 hook detector vẫn là stub `[]`.** Cả 3 trận spar đều
   "MISSED" `fabricated_citation` (8) và `protocol_misuse` (6) dù bằng chứng có sẵn
   trong trace — đây là chỗ có ROI cao nhất nếu muốn tăng điểm nhanh, vì RULES.md §4
   cho tối đa 4 claim/exchange, 1/family — chỉ cần cài đúng vài hook nặng nhất
   (`fabricated_citation` 8, `protocol_misuse` 6, `stale_read` 8, `authority_exceeded`
   10) là đã đổi được recall rất nhiều so với 0.059 hiện tại.

### 🟡 Trung bình — cần soát tay, không phải code mới

4. **4 lá bài `atk_03`, `atk_04`, `atk_05`, `atk_09`** — `make validate` không tự xác
   nhận được "held in principle" vì `defense_event` không đúng hình `gateway.denied`.
   Cần tự đọc RULES.md §5 lethality band + tự spar để kiểm tra 4 lá này thật sự "held
   bởi adversary" chứ không phải chỉ trông giống vậy.
5. **`agent/gateway.py` JOB 1 (ROUTE)** — hiện gọi
   `pick_replica(path_id=..., known_drifting=False)` với `known_drifting` **hard-code
   `False`**, tức chưa thực sự tra `drift.json` để biết path nào đang lệch (README §4:
   "day18 thực sự lệch giữa hai replica"). Nếu không tra, ROUTE job không tự bảo vệ
   được `stale_read` (weight 8) — cần xác nhận `strategy.pick_replica`/`gateway.py` có
   nơi khác đọc drift hay không.
6. **Docstring của `Gateway.decide`** vẫn còn câu cũ "This starter forwards EVERYTHING
   ... and denies NOTHING" — không còn đúng với code hiện tại (đã có 2 nhánh deny).
   Không ảnh hưởng điểm nhưng gây hiểu lầm khi đọc lại sau này.

### 🟢 Thấp — việc vận hành, không phải code

7. **`tests/test_gateway.py`** — file mới, 3 test tự viết đều PASS, nhưng **chưa
   `git add`** (vẫn nằm trong `git status` là untracked). Quyết định giữ/bỏ.
8. **`df8c55dabb35.rar`** — file lạ, untracked, nằm ở root repo (10 KB, tên trùng
   `world_id` nhưng đuôi `.rar` chứ không phải `.zip` như README hướng dẫn tải từ
   Releases). Nên kiểm tra nguồn gốc file này trước khi commit — có thể là artifact
   thử nghiệm cần dọn, không phải một phần bài nộp.
9. **`make submit TEAM=...`** — chưa chạy, đúng như dự định (khoá `agent/`+`deck/`).
   Chỉ nên chạy sau khi giải quyết xong mục 🔴 ở trên, vì sau khi submit,
   `agent/`+`deck/` bị lock.

---

## Tóm tắt cho bạn

- Repo chạy được đầy đủ pipeline: install → doctor → spar → test → validate, không có lỗi thật nào
  do code của bạn gây ra (4 test fail là do thiếu `sandbox-exec` trên Linux, môi trường chứ không
  phải bug).
- **Task 3 (Defend/`gateway.py`)**: đã có tiến triển thật, thắng rookie và operator dứt điểm; thua
  adversary (0–78) — cần xem lại các lỗ hổng còn lại trong `guardrails.py` (3 stub) vì adversary
  chuyên khai thác đúng những lớp mà guardrail chưa che (`guardrail_breach`, có thể cả
  `privacy_leak`/`unsupported_precision`).
- **Task 2 (Prosecute/`eval/prosecute.py`)**: gần như trống — 16/17 lớp lỗi chưa cài, nên cả 3 trận
  đều bỏ lỡ sát thương miễn phí đáng kể (`fabricated_citation` weight 8, `protocol_misuse` weight
  6). Đây là chỗ có ROI implementation cao nhất nếu muốn cải thiện điểm số nhanh.
- **Task 1 (Attack/`deck/`)**: hợp lệ, nhưng 4/10 lá cần soát tay thủ công vì proxy không tự xác
  nhận được "held in principle".
- Chưa nộp bài (`make submit`) — để bạn chủ động khi sẵn sàng khoá `agent/`+`deck/`.

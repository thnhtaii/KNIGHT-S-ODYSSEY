# Cải tiến UI hiển thị AI Performance Stats cho Level 6

Để đáp ứng yêu cầu hiển thị bảng đánh giá hiệu suất của AI sau khi kết thúc Màn 6 (cho cả khi thắng lẫn thua), tương tự như hình mẫu bạn gửi, tôi đề xuất thiết kế bảng **"AI PERFORMANCE STATS - LEVEL 6"** với các tiêu chí được tinh chỉnh riêng biệt dành cho các thuật toán tìm kiếm đối kháng phức tạp mà Boss Robot đang sử dụng.

## Tiêu chí đánh giá đề xuất (Criteria)

Màn 6 không sử dụng tìm đường đơn thuần (như BFS/DFS của Slime) mà sử dụng các thuật toán cây trò chơi (Minimax và Expectimax) để đánh giá chiến thuật. Do đó, bảng thống kê sẽ có cấu trúc như sau:

| Hệ thống AI (Thuật toán) | Tổng số trạng thái đã duyệt (Nodes) | Số nhánh bị cắt (Alpha-Beta Pruned) | Tổng sát thương gây ra |
| :--- | :--- | :--- | :--- |
| **Phase 1 (Minimax)** | [Nodes duyệt ở P1] | N/A | [Sát thương P1] |
| **Phase 2 (Alpha-Beta)** | [Nodes duyệt ở P2] | [Số nhánh bị cắt ở P2] | [Sát thương P2] |
| **Phase 3 (Expectimax)** | [Nodes duyệt ở P3] | N/A | [Sát thương P3 + Thiên thạch] |

### Chi tiết các chỉ số:
1. **Hệ thống AI (Thuật toán)**: Chia làm 3 dòng tương ứng với 3 thuật toán thực tế mà Boss dùng ở từng Phase:
   - **Phase 1 (Minimax)**: Thuật toán cơ bản duyệt độ sâu 3 (khi HP Boss > 70%).
   - **Phase 2 (Alpha-Beta)**: Thuật toán Minimax được tối ưu hoá cắt tỉa nhánh duyệt độ sâu 6 (khi HP Boss 30% - 70%).
   - **Phase 3 (Expectimax)**: Thuật toán xử lý rủi ro tính toán xác suất né tia sét/thiên thạch (khi HP Boss < 30%).
2. **Tổng số trạng thái đã duyệt (Nodes)**: Thể hiện rõ khối lượng tính toán. Chắc chắn Phase 2 sẽ duyệt rất nhiều node nhưng lại nhanh nhờ Alpha-Beta.
3. **Số nhánh bị cắt (Alpha-Beta Pruned)**: Chỉ áp dụng cho Phase 2 (Alpha-Beta). Khẳng định hiệu suất tối ưu của thuật toán này so với Minimax thuần túy.
4. **Tổng sát thương gây ra**: Cho thấy thuật toán nào mang lại sự nguy hiểm cao nhất cho người chơi.

> [!IMPORTANT]
> **Theo dõi dữ liệu tích lũy**
> Hiện tại, game chỉ hiển thị Node Evaluated theo từng giây (Real-time). Tôi sẽ cần thêm các biến để "cộng dồn" (Accumulate) các thông số này trong suốt quá trình người chơi đánh Boss.

## User Review Required
> [!NOTE]
> Bạn xem các tiêu chí (Cột) và đối tượng (Dòng) mà tôi đề xuất ở trên có hợp lý và đúng với ý tưởng của bạn cho Màn 6 chưa? Nếu bạn muốn thêm bớt chỉ số nào (ví dụ: Tốc độ suy nghĩ trung bình, Tỷ lệ đánh trúng...), hãy cho tôi biết nhé!

## Các bước triển khai (Proposed Changes)

1. **Thêm biến tích luỹ vào `battle_level6.py`**:
   - Nhóm Nodes: `total_minimax_nodes`, `total_alphabeta_nodes`, `total_expectimax_nodes`.
   - Nhóm Pruned: `total_alphabeta_pruned`.
   - Nhóm Sát thương: `damage_phase1`, `damage_phase2`, `damage_phase3`.
2. **Thu thập dữ liệu theo Phase**:
   - Ở đầu hàm `update()`, dựa vào `boss.health` để biết đang ở Phase nào, từ đó cộng dồn `ai_nodes_evaluated` và sát thương vào đúng biến của Phase đó.
   - Tương tự cộng dồn `ai_pruned_branches` cho Phase 2.
3. **Tạo file UI mới `ai_stats_level6.py`**:
   - Lập trình một màn hình overlay giống hệt ảnh bạn cung cấp, với bảng grid 4 cột, 3 dòng dữ liệu, thiết kế chuẩn e-Sport như ý bạn.
4. **Hiển thị sau khi kết thúc game**:
   - Chỉnh sửa logic khi `player.health <= 0` hoặc `boss.health <= 0` trong `battle_level6.py`.
   - Trước khi nhảy sang màn hình `GameOverScreen` hoặc `GameVictoryScreen`, sẽ hiển thị `AIStatsLevel6Screen` để người chơi xem. Khi ấn `ENTER`, mới chuyển sang màn hình Thắng/Thua chính thức.

---
## Verification Plan
- Chủ động chơi thử Màn 6 và cố tình để Boss đánh/thả đá trúng.
- Giết Boss hoặc để Player chết.
- Kiểm tra xem màn hình AI PERFORMANCE STATS có hiện lên với các con số tăng dần hợp lý (không bị số 0 tròn trĩnh) hay không.
- Xác nhận bấm ENTER để chuyển tiếp bình thường.

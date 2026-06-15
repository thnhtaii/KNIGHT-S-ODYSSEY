# Stickman Battle

## Giới thiệu

**Stickman Battle** là trò chơi hành động 2D. Người chơi điều khiển nhân vật Stickman chiến đấu với các quái vật trong các màn chơi đa dạng, với hệ thống AI hỗ trợ di chuyển và chiến đấu thông minh. Trò chơi ứng dụng các thuật toán trí tuệ nhân tạo (AI) để tối ưu hóa hành vi nhân vật và kẻ địch, mang lại trải nghiệm chơi mượt mà, thử thách và hấp dẫn.

---

## Tính năng nổi bật

- Nhân vật Stickman có thể di chuyển, nhảy, tấn công và phòng thủ với hoạt ảnh mượt mà.
- Quái vật tự động di chuyển, truy đuổi người chơi nhờ các thuật toán tìm đường thông minh.
- Hệ thống nâng cấp vũ khí thông minh dựa trên thuật toán Decision Tree.
- Bản đồ game đọc từ file `.tmx` đa layer, tạo môi trường chơi phong phú.
- Camera theo sát nhân vật, giao diện trực quan, thân thiện với người dùng.

---

## Công nghệ sử dụng

- Ngôn ngữ: **Python 3.10+**
- Thư viện:
  - [Pygame](https://www.pygame.org/) - phát triển game 2D
  - [pytmx](https://github.com/bitcraft/pytmx) - đọc file bản đồ `.tmx`
  - [NumPy](https://numpy.org/) - xử lý toán học, khoảng cách
  - [Matplotlib](https://matplotlib.org/) - hỗ trợ phân tích (ngoài game)
- IDE gợi ý: Visual Studio Code, PyCharm

---

## Các thuật toán AI pathfinding và hành vi sử dụng trong game

Trong game Stickman Battle, các thuật toán trí tuệ nhân tạo được sử dụng để điều khiển hành vi di chuyển và chiến đấu của nhân vật và quái vật, gồm:

1. **BFS (Breadth-First Search)**Tìm đường đi ngắn nhất trong môi trường grid không trọng số, dùng để truy đuổi hoặc di chuyển an toàn.
2. **Greedy Best-First Search**Sử dụng heuristic Manhattan để đi nhanh về đích, hiệu quả trong tìm đường với chi phí thấp.
3. **Hill Climbing Step**Tính bước di chuyển tiếp theo dựa trên giảm thiểu khoảng cách đến đích, đơn giản và nhanh gọn.
4. **Backtracking Pathfinding**Tìm đường đi bằng phương pháp đệ quy quay lui, thích hợp cho môi trường nhỏ hoặc khi cần tìm tất cả đường đi.
5. **Q-Learning**Thuật toán học củng cố giúp nhân vật học dần cách chọn hành động tối ưu qua các lần chơi, tăng khả năng tự thích nghi.
6. **And-Or Search**
   Tìm kiếm dạng cây quyết định, dùng trong môi trường phức tạp, đảm bảo không bỏ sót lựa chọn.
   **

## So sánh các thuật toán AI trong game

| Thuật toán            | Ưu điểm chính                                                                              | Nhược điểm chính                                                        | Ứng dụng phù hợp trong game                                       | Hiệu suất & Độ phức tạp                                              | Ghi chú về mô hình xác suất 70:30 (Uncertainty)                                                                                               |
| ----------------------- | ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **BFS**           | - Tìm đường đi ngắn nhất `<br>`- Khám phá toàn diện, không bỏ sót trạng thái | - Tốn bộ nhớ và thời gian khi không gian trạng thái lớn             | Truy đuổi, di chuyển quái vật Slime theo cách chính xác       | Thời gian: O(V+E)`<br>`Độ sâu: O(b^d), b = branching, d = depth sâu | Không thích hợp môi trường xác suất, chỉ tốt cho trạng thái hiện tại                                                                  |
|                         |                                                                                                |                                                                              |                                                                       |                                                                            |                                                                                                                                                     |
| **Greedy Search** | - Xử lý nhanh, đơn giản `<br>`- Triển khai dễ `<br>`- Dễ rơi vào cực bộ        | - Không đảm bảo tối ưu toàn cục, dễ kẹt tại cực bộ              | Phản ứng nhanh trong tình huống khẩn cấp                        | Thời gian thấp, độ phức tạp thấp                                    | Không tốt với môi trường xác suất, không phải thuật toán heuristic                                                                      |
| **Backtracking**  | - Toàn diện, kiểm tra mọi lựa chọn `<br>`- Linh hoạt nếu ràng buộc chính xác     | - Tiêu tốn thời gian, xử lý chậm                                       | Tìm chuỗi hành động logic, chiến thuật phức tạp              | Thời gian tối đa O(b^d) hoặc O(d*d)                                    | Nếu định nghĩa ràng buộc theo xác suất → chạy không đúng hoặc chậm                                                                   |
| **And-Or Search** | - Mô hình hóa chiến lược ra quyết định `<br>`- Tăng tính linh hoạt hành vi      | - Phức tạp, tốn tài nguyên tính toán                                  | Xây dựng hệ thống phối hợp hành động chiến lược đa dạng | Thời gian và độ phức tạp cao, phụ thuộc cấu trúc cây            | Có thể kết hợp mô hình xác suất:`<br>`70:30 để phân nhánh theo xác suất:`<br>`- 70% chọn `And<br>`- 30% rẽ nhánh không xác |
| **Hill Climbing** | - Đơn giản, nhanh chóng `<br>`- Tối ưu nhanh nếu gần cực đại                      | - Dễ bị kẹt tại cực bộ `<br>`- Không đảm bảo tối ưu toàn cục | Tối ưu các hành động nhỏ, lựa chọn bước đi chiến thuật  | Thời gian thấp, độ phức tạp thấp                                    | Không mô hình tốt cho xác suất, không đảm bảo tính khám phá toàn cục                                                                 |

---

## Hướng dẫn cài đặt và chạy game

1. Cài đặt thư viện cần thiết:
   ```bash
   pip install pygame pytmx base64
   ```
2. Chạy game:
   ```bash
   python main.py

   ```

---

## Cấu trúc thư mục

- assets        # Tài nguyên hình ảnh, âm thanh
- levels        # File bản đồ .tmx
- src           # Mã nguồn game và AI
- main.py       # File chạy chính
- README.md     # Tệp hướng dẫn này

---

## DEMO

- Màn hình Start game `<br>`
  ![Màn hình Start game](https://drive.google.com/uc?export=view&id=1tmrfYMf8bXFAwjqoaOx9CSzzTHhWYamr)
- Màn hình Level 1 `<br>`
  ![Màn hình Level 1](https://drive.google.com/uc?export=view&id=1N6b_rr1CJldaqouGwajteCOM0-r5JoFb)
- Slime phát hiện nhân vật và truy đuổi `<br>`
  ![Slime phát hiện nhân vật và truy đuổi](https://drive.google.com/uc?export=view&id=12g5ArVkgawkH8rNpB4f9-TYcIwpSjDPf)
- Màn hình Game over `<br>`
  ![Màn hình Game over](https://drive.google.com/uc?export=view&id=1eY63pPhHLE09zdcsVAv_lI3yYsekZYe5)
- Nhân vật có thể đánh Slime và Màn hình Win game `<br>`
  ![Màn hình Win game](https://drive.google.com/uc?export=view&id=1qTmS9K0h1CVkPTgfiAXGvsZnxGhkakYy)
- Sau khi Win Level 1 sẽ mở khóa Level 2 `<br>`
  ![Sau khi Win Level 1 sẽ mở khóa Level 2](https://drive.google.com/uc?export=view&id=1Us4qlKKgbdlshniS9m-ce5xYkg6VzPrn)

---

## Kết quả và đánh giá

- Game chạy ổn định, không gặp lỗi.
- Nhân vật chính di chuyển, nhảy, tấn công mượt mà, va chạm hợp lý với môi trường.
- Camera theo sát nhân vật mượt mà không bị lag.
- AI Slime có hành vi linh hoạt, truy đuổi và phản ứng hợp lý với nhân vật Stickman.
- Giao diện game trực quan, thân thiện với người chơi.

## Những khó khăn gặp phải

- Sai lệch trong tính toán camera_offset dẫn đến bản đồ bị lệch khi hiển thị.
- Xử lý va chạm phức tạp giữa các đối tượng, đặc biệt khi nhân vật nhảy hoặc leo bậc thang.
- Đồng bộ hoạt ảnh khi tấn công hoặc chuyển trạng thái không mượt do frame animation chưa tối ưu.
- Khó xác định mặt đất chính xác khi bản đồ có nhiều layer chồng lên nhau.

## Định hướng phát triển tiếp theo

- Thêm hệ thống HUD hiển thị thanh máu, tên nhân vật, chỉ số kỹ năng theo thời gian thực.
- Phát triển thêm nhiều màn chơi, đa dạng bản đồ, hỗ trợ chuyển cảnh (portal/door).
- Nâng cao AI Slime để có thể tự động di chuyển, tấn công, phòng thủ theo phạm vi.
- Cải thiện vật lý game như nhảy, leo thang, xử lý va chạm góc cạnh thực tế hơn.
- Tối ưu hiệu suất để giảm flickering và tăng tốc độ render.

## Tài liệu tham khảo

- [StickMan_Game GitHub](https://github.com/nguyenhuytlu/StickMan_Game)
- [StickMan Game Development Series YouTube Playlist](https://www.youtube.com/playlist?list=PLjcN1EyupaQm20hlUE11y9y8EY2aXLpnv)

---

## Tác giả

- Giảng viên hướng dẫn: TS. Phan Thị Huyền Trang
- Nhóm SV thực hiện: Nhóm 04
  - Lê Chí Quốc - 24110313
  - Lê Huỳnh Phong - 24110302
  - Đỗ Thanh Thành Tài - 24133050
- Mã lớp học: 252ARIN330585_08

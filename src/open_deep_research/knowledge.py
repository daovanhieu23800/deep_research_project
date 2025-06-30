dataset_info = """

Schema for table shipping_order:
| Field | Type | Description |
|---|---|---|
| created_date_partition | DATE | Cột phân vùng theo ngày tạo (must have when query into this table) |
| _id | STRING | mã mongo |
| return_ward_code | STRING | phường trả |
| return_district_id | INTEGER | quận trả |
| from_ward_code | STRING | mã phường người gửi |
| from_district_id | INTEGER | quận người gửi |
| from_location | STRING | vị trí người gửi (gồm thông tin lat, long, cell_code, wardcode, trustlevel) |
| deliver_station_id | INTEGER | mã bưu cục/kho bàn giao hàng cho người nhận |
| to_ward_code | STRING | mã phường người nhận Buyer |
| to_district_id | INTEGER | mã quận người nhận Buyer |
| to_location | STRING | vị trí người nhận (gồm thông tin lat, long, cell_code, wardcode, trustlevel) Buyer |
| weight | INTEGER | cân nặng (gram) |
| length | INTEGER | dài (cm) |
| width | INTEGER | rộng (cm) |
| height | INTEGER | cao (cm) |
| converted_weight | INTEGER | khối lượng quy đổi (gram) |
| service_type_id | INTEGER | loại dịch vụ |
| service_id | INTEGER | gói cước |
| payment_type_id | INTEGER | hình thức thay toán - người nhận trả hay người gửi trả |
| custom_service_fee | INTEGER |  |
| cod_amount | INTEGER | số tiền cod của đơn hàng |
| cod_collect_date | TIMESTAMP | ngày tạo phiếu thu cod |
| cod_transfer_date | TIMESTAMP | ngày chuyển cod |
| insurance_value | INTEGER | giá trị khai giá bảo hiểm |
| pick_station_id | INTEGER | bưu cục nhận hàng |
| client_order_code | STRING | mã đơn hàng khách hàng |
| pickup_time_before | TIMESTAMP |  |
| pickup_time_after | TIMESTAMP |  |
| required_note | STRING | ghi chú bắt buộc |
| content | STRING | nội dung hàng hóa |
| note | STRING | ghi chú |
| coupon | STRING | coupon áp dụng cho đơn hàng |
| version_no | STRING | số phiên bản |
| updated_ip | STRING | ip cập nhật |
| updated_employee | INTEGER | mã nhân viên cập nhật |
| updated_date | TIMESTAMP | thời gian cập nhật cuối DATETIME_KEY +1 |
| created_ip | STRING | mã ip tạo đơn |
| created_employee | INTEGER | nhân viên tạo đơn - nhân viên của ghn tạo đơn giúp |
| created_date | TIMESTAMP | ngày tạo đơn +2 |
| status | STRING | trạng thái đơn hàng |
| pick_warehouse_id | INTEGER | mã kho lấy |
| deliver_warehouse_id | INTEGER | mã kho giao |
| current_warehouse_id | INTEGER | mã kho hiện tại |
| return_warehouse_id | INTEGER | mã kho trả |
| next_warehouse_id | INTEGER | kho tiếp theo sẽ đến |
| leadtime | TIMESTAMP | thời gian dự kiến giao hàng |
| order_date | TIMESTAMP | ngày tạo đơn cut off |
| action | STRING | thao tác (chi tiết hơn trạng thái) |
| soc_id | STRING | mã cước |
| finish_date | TIMESTAMP |  |
| legacy | BOOLEAN | có phải hệ thống cũ |
| tag | STRING | nhãn |
| pickup_time | TIMESTAMP | thời gian hẹn lấy |
| warehouse_log | STRING | log thay đổi kho |
| is_partial_return | BOOLEAN | đơn giao trả 1 phần |
| items | STRING | items chi tiết trong đơn |
| pick_shift | STRING | ca lấy |
| deliver_shift | STRING | ca giao |
| return_shift | STRING | ca trả hàng |
| sort_code | STRING | mã phân loại |
| first_picked_time | TIMESTAMP | thời gian lấy đầu tiên |
| lost_time | TIMESTAMP | thời gian mất hàng |
| num_pick | INTEGER | số lần lấy |
| num_deliver | INTEGER | số lần giao |
| num_return | INTEGER | số lần trả |
| pick_user | INTEGER | nhân viên lấy Driver |
| deliver_user | INTEGER | mã nhân viên giao hàng Driver |
| return_user | INTEGER | nhân viên trả Driver |
| lost_user | INTEGER | người xác nhận mất hàng |
| end_pick_time | TIMESTAMP | thời gian kết thúc lấy |
| first_delivered_time | TIMESTAMP | thời gian giao hàng đầu tiên |
| return_time | TIMESTAMP | thời gian hẹn trả |
| s2r_time | TIMESTAMP | thời gian bắt đầu tính để chờ chuyển trả hàng |
| end_delivery_time | TIMESTAMP | thời gian kết thúc giao |
| end_return_time | TIMESTAMP | thời gian kết thúc trả |
| end_success_time | TIMESTAMP | thời gian hoàn tất đơn hàng (GTTC) |
| updated_warehouse | INTEGER | mã kho cập nhất |
| current_transport_warehouse_id | INTEGER | mã kho hiện tại đang luân chuyển đến |
| internal_process | STRING |  |
| table_partition | STRING |  |
| extra_service | STRING | dịch vụ bổ sung |
| cod_failed_amount | INTEGER | tiền giao thất bại thu khách |
| cod_failed_collect_date | TIMESTAMP | ngày thu tiền giao thất bại của khách |
| pods | STRING | chứng từ giao nhận |
| discount_log | STRING |  |
| is_b2b | BOOLEAN | đơn B2B |
| cod_transferred_histories | STRING |  |
| is_cod_collected | BOOLEAN | đơn có thu cod không |
| process_by_partner | BOOLEAN | đơn hàng do đối tác xử lí |
| process_partner_name | STRING | tên đối tác xử lý |
| operation_partner | STRING | đối tác vận hành |
| type_order | STRING | loại đơn hàng (phân biệt đơn freight) (Freight hoặc Null) |
| type_order_code | STRING | mã loại đơn hàng (phân biệt các nhóm đơn freight) |
| cod_amount_bk | INTEGER | Số tiền COD bản ghi cũ (backup) |
| ecom_config_fee_id | INTEGER | ID cấu hình phí thương mại điện tử |
| ecom_extra_cost_id | INTEGER | ID chi phí bổ sung thương mại điện tử |
| config_fee_id | INTEGER | ID cấu hình phí |
| extra_cost_id | INTEGER | ID chi phí bổ sung |
| config_fee_id_new | STRING | ID cấu hình phí mới (chuẩn hóa) |
| extra_cost_id_new | STRING | ID chi phí bổ sung mới (chuẩn hóa) |
| is_new_multiple | BOOLEAN | Cờ cho biết đơn hàng nhiều gói (phiên bản mới) |
| order_code_hash | STRING | Giá trị băm của mã đơn hàng (ẩn danh hóa) |
| client_id_hash | INTEGER | Giá trị băm của mã khách hàng (ẩn danh hóa) |
| shop_id_hash | INTEGER | Giá trị băm của mã shop (ẩn danh hóa) |
| updated_client_hash | INTEGER | Giá trị băm của client khi cập nhật |
| created_client_hash | INTEGER | Giá trị băm của client khi tạo |

Schema for table dim_location:
|Field|Type|Description|
|---|---|---|
|ward_id|STRING|Mã phường/xã|
|ward_name|STRING|Tên phường/xã|
|ward_status|INTEGER|Trạng thái phường/xã (0 = ngưng, 1 = hoạt động)|
|district_id|INTEGER|ID quận/huyện|
|district_code|STRING|Mã quận/huyện|
|district_name|STRING|Tên quận/huyện|
|district_type|STRING|Loại quận/huyện (Nội Thành/Ngoại Thành 1/Ngoại Thành 2)|
|province_id|INTEGER|ID tỉnh/thành phố|
|province_name|STRING|Tên tỉnh/thành phố|
|region_id|INTEGER|ID khu vực|
|region_name|STRING|Tên khu vực|
|region_fullname|STRING|Tên vùng đầy đủ|
|region_shortname|STRING|Tên vùng rút gọn|
|region_code_hrw|STRING|Mã vùng HRW|


Schema for table dim_warehouse:
|Field|Type|Description|
|---|---|---|
|warehouse_id|INTEGER|Mã kho|
|department_id|INTEGER|Mã phòng ban|
|warehouse_name|STRING|Tên kho|
|warehouse_address|STRING|Địa chỉ kho|
|is_enabled|BOOLEAN|Trạng thái hoạt động (true/false)|
|status_hrw|INTEGER|Trạng thái hoạt động trên hệ thống HRW (1 đang hoạt động, 0 ngưng)|
|warehouse_type|STRING|Loại kho (BC bưu cục, KTC kho trung chuyển, KHL kho khách)|
|ward_code|STRING|Mã phường/xã|
|ward_name|STRING|Tên phường/xã|
|district_id|INTEGER|Mã quận/huyện|
|district_name|STRING|Tên quận/huyện|
|province_id|INTEGER|Mã tỉnh/thành phố|
|province_name|STRING|Tên tỉnh/thành phố|
|region_shortname|STRING|Tên vùng rút gọn|
|region_fullname|STRING|Tên vùng đầy đủ|
|team_name|STRING|Tên team HRW phụ trách|
|section_name|STRING|Tên section HRW phụ trách|
|department_name|STRING|Tên phòng ban HRW phụ trách|
|gdv_id|INTEGER|Mã Giám đốc vùng|
|gdv_name|STRING|Tên Giám đốc vùng|
|pgdv_id|STRING|Mã Phó Giám đốc vùng|
|pgdv_name|STRING|Tên Phó Giám đốc vùng|
|area_manager_id|INTEGER|Mã Area Manager phụ trách|
|area_manager_name|STRING|Tên Area Manager phụ trách|
|station_leader_id|INTEGER|Mã Trưởng bưu cục|
|station_leader_name|STRING|Tên Trưởng bưu cục|
|latitude|FLOAT|Vĩ độ kho|
|longitude|FLOAT|Kinh độ kho|
|owner_location_id|FLOAT|Mã kho chủ (kho ảo thuộc kho chủ này)|
|is_virtual|BOOLEAN|true kho ảo, false kho vật lý|
|created_time|TIMESTAMP|Thời gian tạo kho|
|last_updated_time|TIMESTAMP|Thời gian cập nhật cuối|
|hrw_updated_at|TIMESTAMP|Thời gian cập nhật cuối trên HRW|

Schema for table middle_mile_log:
|Field|Type|Description|
|---|---|---|
|action_type|STRING|Tên thao tác (must have when query into this table)|
|order_code_hash|STRING|Mã đơn hàng (băm ẩn danh)|
|package_code_hash|STRING|Mã kiện hàng (băm ẩn danh)|
|action_date|DATE|Ngày thao tác|
|action_time|STRING|Giờ thao tác|
|warehouse_id|INTEGER|Mã kho/bưu cục thực hiện thao tác|


Schema for revenue_order:
 - order_code_hash (STRING)
 - rev (FLOAT)



Schema for sla_delivery:
|Field|Type|Description|
|---|---|---|
|route|STRING|Phân loại tuyến|
|from_district|STRING|Tên quận/huyện lấy|
|to_district|STRING|Tên quận/huyện giao|
|from_district_id|INTEGER|Mã định danh quận/huyện lấy|
|to_district_id|INTEGER|Mã định danh quận/huyện giao|
|delivery_sla|INTEGER|Quy định SLA‒số ngày giao|

"""


abbreviation = """
| Thuật ngữ                                | Viết tắt | Giải thích ý nghĩa                                              |
|------------------------------------------|----------|-----------------------------------------------------------------|
| Key Account                              | KA       | Khách hàng lớn                                                  |
| Small Medium Enterprise                  | SME      | Khách hàng vừa và nhỏ                                           |
| Khách Hàng Mới                           | KHM      | KH lần đầu hoặc quay lại sau 90 ngày                            |
| Khách Hàng Cũ                            | KHC      | KH đang sử dụng dịch vụ                                         |
| Nhóm A,B,C,D,E,F                         |         | Phân loại KH theo doanh thu                                     |
| Shop Siêu Sao                            |        | Chương trình khách hàng thân thiết                              |
|                                          |          |                                                                 |
| Nhân viên Phát triển Thị trường          | NVPTTT   | Nhân viên giao nhận (shipper)                                   |
| Chiến Binh Siêu Sao                      | CBSS     | NVPTTT có doanh thu KHM ≥ 1 triệu/tháng                         |
| Đại Hiệp                                  |       | CBSS liên tục 3 tháng                                           |
| Cao Thủ                                   |       | CBSS liên tục 6 tháng                                           |
| Đại Cao Thủ                               |         | CBSS liên tục 9 tháng                                           |
| Chiến Thần                                |         | CBSS liên tục 12 tháng                                          |
| NVPTTT siêu giao                         |         | NV có > 70 % thu nhập từ giao                                   |
| NVPTTT siêu lấy                          |         | (không có giải thích)                                           |
|                                          |          |                                                                 |
| Ban Dự Án                                | BDA      | Nhóm triển khai dự án                                           |
| Area Manager                             | AM       | Quản lý khu vực                                                 |
| Trưởng Bưu Cục                           | TBC      | Quản lý bưu cục                                                 |
| Giám đốc Vùng                            | GĐV      | Giám đốc vùng                                                   |
| Human Resources Business Partner         | HRBP     | Đối tác nhân sự                                                 |
| Nhân viên xử lý                          | NVXL     | Nhân viên xử lý đơn trong kho                                   |
| Compensation & Benefits                  | CnB      | Phòng Tiền lương & Phúc lợi                                     |
| Business Intelligence                    | BI       | Phòng Phân tích dữ liệu                                         |
| Finance                                  | FIN      | Phòng Tài chính                                                 |
| Operational Excellence                   | OE       | Phòng Chiến lược Vận hành                                       |
|                                          |          |                                                                 |
| Đông Bắc Bộ                              | DBB      | Vùng địa lý                                                     |
| Bắc Trung Bộ                             | BTB      | Vùng địa lý                                                     |
| Tây Bắc Bộ                               | TBB      | Vùng địa lý                                                     |
| Duyên hải                                | DSH      | Vùng địa lý                                                     |
| Đông Nam Bộ                              | DNB      | Vùng địa lý                                                     |
| Nam Trung Bộ                             | NTB      | Vùng địa lý                                                     |
| Tây Nam Bộ                               | TNB      | Vùng địa lý                                                     |
| Hồ Chí Minh                              | HCM      | Vùng địa lý                                                     |
| Hà Nội                                   | HNO      | Vùng địa lý                                                     |
|                                          |          |                                                                 |
| Giao Thành Công                          | GTC      | Trạng thái giao hàng thành công                                 |
| Lấy Thành Công                           | LTC      | Trạng thái lấy hàng thành công                                  |
| Giao Thất Bại - Thu tiền                 | GTB-TT   | Giao không thành công lần thứ 3 - thu tiền                      |
| Stop                                     |         | Đơn vị quy đổi (1 Stop = 4 kg)                                  |
| Giao-Lấy Hỗn Hợp                         | GLHH     | Mô hình giao lấy kết hợp                                        |
| Kho Khách Hàng Lớn                       | KHL      | Mô hình kho riêng cho KH lớn                                    |
| Bưu cục Hybrid                           |         | BC kết hợp nhiều tuyến                                          |
| Giao Ca 2                                |         | Mô hình giao 2 ca/ngày                                          |
| Chia tuyến                               |         | Phân chia địa bàn hoạt động                                     |
| “Cứu bể”                                 |         | Giải pháp khắc phục BC bất ổn                                   |
| Standard Operating Procedure             | SOP      | Quy trình chuẩn                                                 |
|                                          |          |                                                                 |
| Lương Hoa Hồng                           |        | Cách tính lương theo % doanh thu                                |
| Lương Đơn Hàng                           |         | Cách tính lương cũ theo khối lượng                              |
| Auto-payroll                             |         | Hệ thống tính lương tự động                                     |
| Payslip                                  |         | Bảng lương chi tiết                                             |
| Kỳ lương                                  |         | Chu kỳ trả lương (2 kỳ/tháng)                                   |
|                                          |          |                                                                 |
| Electronic Know Your Customer            | eKYC     | Xác minh khách hàng điện tử                                     |
| Talent Management System                 |         | Hệ thống quản trị nhân tài                                      |
| Bảng xếp hạng vùng                       |        | Xếp hạng hiệu quả các vùng                                      |
| Dự án 7K                                 | 7K       | Dự án Toàn dân bán hàng                                         |
| Quy hoạch bưu cục                        |         | Kế hoạch tổ chức BC                                             |

"""
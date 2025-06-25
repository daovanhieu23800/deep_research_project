dataset_info = """
Schema for dim_location:
 - ward_id (STRING)
 - ward_name (STRING)
 - ward_status (INTEGER)
 - district_id (INTEGER)
 - district_code (STRING)
 - district_name (STRING)
 - district_type (STRING)
 - province_id (INTEGER)
 - province_name (STRING)
 - region_id (INTEGER)
 - region_name (STRING)
 - region_fullname (STRING)
 - region_shortname (STRING)
 - region_code_hrw (STRING)

Schema for dim_warehouse:
 - warehouse_id (INTEGER)
 - department_id (INTEGER)
 - warehouse_name (STRING)
 - warehouse_address (STRING)
 - is_enabled (BOOLEAN)
 - status_hrw (INTEGER)
 - warehouse_type (STRING)
 - ward_code (STRING)
 - ward_name (STRING)
 - district_id (INTEGER)
 - district_name (STRING)
 - province_id (INTEGER)
 - province_name (STRING)
 - region_shortname (STRING)
 - region_fullname (STRING)
 - team_name (STRING)
 - section_name (STRING)
 - department_name (STRING)
 - gdv_id (INTEGER)
 - gdv_name (STRING)
 - pgdv_id (STRING)
 - pgdv_name (STRING)
 - area_manager_id (INTEGER)
 - area_manager_name (STRING)
 - station_leader_id (INTEGER)
 - station_leader_name (STRING)
 - latitude (FLOAT)
 - longitude (FLOAT)
 - owner_location_id (FLOAT)
 - is_virtual (BOOLEAN)
 - created_time (TIMESTAMP)
 - last_updated_time (TIMESTAMP)
 - hrw_updated_at (TIMESTAMP)

Schema for middle_mile_log:
 - action_type (STRING)
 - order_code_hash (STRING)
 - package_code_hash (STRING)
 - action_date (DATE)
 - action_time (STRING)
 - warehouse_id (INTEGER)

Schema for revenue_order:
 - order_code_hash (STRING)
 - rev (FLOAT)

Schema for shipping_order:
 - created_date_partition (DATE)
 - _id (STRING)
 - return_ward_code (STRING)
 - return_district_id (INTEGER)
 - from_ward_code (STRING)
 - from_district_id (INTEGER)
 - from_location (STRING)
 - deliver_station_id (INTEGER)
 - to_ward_code (STRING)
 - to_district_id (INTEGER)
 - to_location (STRING)
 - weight (INTEGER)
 - length (INTEGER)
 - width (INTEGER)
 - height (INTEGER)
 - converted_weight (INTEGER)
 - service_type_id (INTEGER)
 - service_id (INTEGER)
 - payment_type_id (INTEGER)
 - custom_service_fee (INTEGER)
 - cod_amount (INTEGER)
 - cod_collect_date (TIMESTAMP)
 - cod_transfer_date (TIMESTAMP)
 - insurance_value (INTEGER)
 - pick_station_id (INTEGER)
 - client_order_code (STRING)
 - pickup_time_before (TIMESTAMP)
 - pickup_time_after (TIMESTAMP)
 - required_note (STRING)
 - content (STRING)
 - note (STRING)
 - coupon (STRING)
 - version_no (STRING)
 - updated_ip (STRING)
 - updated_employee (INTEGER)
 - updated_date (TIMESTAMP)
 - created_ip (STRING)
 - created_employee (INTEGER)
 - created_date (TIMESTAMP)
 - status (STRING)
 - pick_warehouse_id (INTEGER)
 - deliver_warehouse_id (INTEGER)
 - current_warehouse_id (INTEGER)
 - return_warehouse_id (INTEGER)
 - next_warehouse_id (INTEGER)
 - leadtime (TIMESTAMP)
 - order_date (TIMESTAMP)
 - action (STRING)
 - soc_id (STRING)
 - finish_date (TIMESTAMP)
 - legacy (BOOLEAN)
 - tag (STRING)
 - pickup_time (TIMESTAMP)
 - warehouse_log (STRING)
 - is_partial_return (BOOLEAN)
 - items (STRING)
 - pick_shift (STRING)
 - deliver_shift (STRING)
 - return_shift (STRING)
 - sort_code (STRING)
 - first_picked_time (TIMESTAMP)
 - lost_time (TIMESTAMP)
 - num_pick (INTEGER)
 - num_deliver (INTEGER)
 - num_return (INTEGER)
 - pick_user (INTEGER)
 - deliver_user (INTEGER)
 - return_user (INTEGER)
 - lost_user (INTEGER)
 - end_pick_time (TIMESTAMP)
 - first_delivered_time (TIMESTAMP)
 - return_time (TIMESTAMP)
 - s2r_time (TIMESTAMP)
 - end_delivery_time (TIMESTAMP)
 - end_return_time (TIMESTAMP)
 - end_success_time (TIMESTAMP)
 - updated_warehouse (INTEGER)
 - current_transport_warehouse_id (INTEGER)
 - internal_process (STRING)
 - table_partition (STRING)
 - extra_service (STRING)
 - cod_failed_amount (INTEGER)
 - cod_failed_collect_date (TIMESTAMP)
 - pods (STRING)
 - discount_log (STRING)
 - is_b2b (BOOLEAN)
 - cod_transferred_histories (STRING)
 - is_cod_collected (BOOLEAN)
 - process_by_partner (BOOLEAN)
 - process_partner_name (STRING)
 - operation_partner (STRING)
 - type_order (STRING)
 - type_order_code (STRING)
 - cod_amount_bk (INTEGER)
 - ecom_config_fee_id (INTEGER)
 - ecom_extra_cost_id (INTEGER)
 - config_fee_id (INTEGER)
 - extra_cost_id (INTEGER)
 - config_fee_id_new (STRING)
 - extra_cost_id_new (STRING)
 - is_new_multiple (BOOLEAN)
 - order_code_hash (STRING)
 - client_id_hash (INTEGER)
 - shop_id_hash (INTEGER)
 - updated_client_hash (INTEGER)
 - created_client_hash (INTEGER)

Schema for sla_delivery:
 - route (STRING)
 - from_district (STRING)
 - to_district (STRING)
 - from_district_id (INTEGER)
 - to_district_id (INTEGER)
 - delivery_sla (INTEGER)"""


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
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from open_deep_research.utils import query_bigquery

# Input model for schema retrieval tools. It's empty as no input is needed.
class GetSchemaInput(BaseModel):
    """Input to a schema retrieval tool. No parameters are needed."""
    pass
class UniqueValueInput(BaseModel):
    column: str = Field(..., description="Column name to inspect")
    table:  str = Field(..., description="Table containing the column, it should be in format 'agentic-ai-463517.ghn_data.<table_name>'")

@tool(args_schema=GetSchemaInput)
def get_schema_shipping_order() -> str:
    """
    Returns the DDL schema for the `shipping_order` table.
    Call this tool to see the exact column names, data types, and descriptions for the main transaction table.
    """
    return SHIPPING_ORDER_SCHEMA_DDL

@tool(args_schema=GetSchemaInput)
def get_schema_dim_location() -> str:
    """
    Returns the DDL schema for the dim_location table.
    Call this tool to see columns related to geographic information like districts, provinces, and regions.
    """
    return DIM_LOCATION_SCHEMA_DDL

@tool(args_schema=GetSchemaInput)
def get_schema_dim_warehouse() -> str:
    """
    Returns the DDL schema for the `dim_warehouse` table.
    Call this tool to see columns related to warehouses, pickup stations, and their management structure.
    """
    return DIM_WAREHOUSE_SCHEMA_DDL

@tool(args_schema=GetSchemaInput)
def get_schema_middle_mile_log() -> str:
    """
    Returns the DDL schema for the `middle_mile_log` table.
    Call this tool to see columns related to package movements between warehouses.
    """
    return MIDDLE_MILE_LOG_SCHEMA_DDL

@tool(args_schema=GetSchemaInput)
def get_schema_revenue_order() -> str:
    """
    Returns the DDL schema for the `revenue_order` table.
    Call this tool to see columns for order revenue.
    """
    return REVENUE_ORDER_SCHEMA_DDL

@tool(args_schema=GetSchemaInput)
def get_schema_sla_delivery() -> str:
    """
    Returns the DDL schema for the `sla_delivery` table.
    Call this tool to see columns related to Service Level Agreements (SLA) for delivery routes.
    """
    return SLA_DELIVERY_SCHEMA_DDL

@tool(args_schema=UniqueValueInput)
def get_unique_value_of_columns(column: str, table: str) -> str:
    """
    Returns all unique value of a column in the table
    Call this tool to see all uniques value of one 
    """
    query = f"""SELECT DISTINCT {column}
FROM   `{table}`
WHERE  {column} IS NOT NULL"""

    if table == "agentic-ai-463517.ghn_data.shipping_order":
        query += """ AND created_date_partition <'2030-01-01' """
    elif table == "agentic-ai-463517.ghn_data.middle_mile_log":
        query += """ AND action_date <'2030-01-01' """
    #print('====================test tool========================')
    #print(query)
    result = query_bigquery(query)
    #print(result)
    #print('====================test tool========================')
    return f"All unique value of {column}: {result}"


# --- Define the static DDL schema string for shipping_order --- 
SHIPPING_ORDER_SCHEMA_DDL = """
CREATE TABLE shipping_order (
    created_date_partition DATE COMMENT 'Cột phân vùng theo ngày tạo (must have when query into this table)',
    _id STRING COMMENT 'mã mongo',
    return_ward_code STRING COMMENT 'phường trả',
    return_district_id INTEGER COMMENT 'quận trả',
    from_ward_code STRING COMMENT 'mã phường người gửi',
    from_district_id INTEGER COMMENT 'quận người gửi',
    from_location STRING COMMENT 'vị trí người gửi (gồm thông tin lat, long, cell_code, wardcode, trustlevel)',
    deliver_station_id INTEGER COMMENT 'mã bưu cục/kho bàn giao hàng cho người nhận',
    to_ward_code STRING COMMENT 'mã phường người nhận Buyer',
    to_district_id INTEGER COMMENT 'mã quận người nhận Buyer',
    to_location STRING COMMENT 'vị trí người nhận (gồm thông tin lat, long, cell_code, wardcode, trustlevel) Buyer',
    weight INTEGER COMMENT 'cân nặng (gram)',
    length INTEGER COMMENT 'dài (cm)',
    width INTEGER COMMENT 'rộng (cm)',
    height INTEGER COMMENT 'cao (cm)',
    converted_weight INTEGER COMMENT 'khối lượng quy đổi (gram)',
    service_type_id INTEGER COMMENT 'loại dịch vụ',
    service_id INTEGER COMMENT 'gói cước',
    payment_type_id INTEGER COMMENT 'hình thức thay toán - người nhận trả hay người gửi trả',
    custom_service_fee INTEGER COMMENT '',
    cod_amount INTEGER COMMENT 'số tiền cod của đơn hàng',
    cod_collect_date TIMESTAMP COMMENT 'ngày tạo phiếu thu cod',
    cod_transfer_date TIMESTAMP COMMENT 'ngày chuyển cod',
    insurance_value INTEGER COMMENT 'giá trị khai giá bảo hiểm',
    pick_station_id INTEGER COMMENT 'bưu cục nhận hàng',
    client_order_code STRING COMMENT 'mã đơn hàng khách hàng',
    pickup_time_before TIMESTAMP COMMENT '',
    pickup_time_after TIMESTAMP COMMENT '',
    required_note STRING COMMENT 'ghi chú bắt buộc',
    content STRING COMMENT 'nội dung hàng hóa',
    note STRING COMMENT 'ghi chú',
    coupon STRING COMMENT 'coupon áp dụng cho đơn hàng',
    version_no STRING COMMENT 'số phiên bản',
    updated_ip STRING COMMENT 'ip cập nhật',
    updated_employee INTEGER COMMENT 'mã nhân viên cập nhật',
    updated_date TIMESTAMP COMMENT 'thời gian cập nhật cuối DATETIME_KEY +1',
    created_ip STRING COMMENT 'mã ip tạo đơn',
    created_employee INTEGER COMMENT 'nhân viên tạo đơn - nhân viên của ghn tạo đơn giúp',
    created_date TIMESTAMP COMMENT 'ngày tạo đơn +2',
    status STRING COMMENT 'trạng thái đơn hàng',
    pick_warehouse_id INTEGER COMMENT 'mã kho lấy',
    deliver_warehouse_id INTEGER COMMENT 'mã kho giao',
    current_warehouse_id INTEGER COMMENT 'mã kho hiện tại',
    return_warehouse_id INTEGER COMMENT 'mã kho trả',
    next_warehouse_id INTEGER COMMENT 'kho tiếp theo sẽ đến',
    leadtime TIMESTAMP COMMENT 'thời gian dự kiến giao hàng',
    order_date TIMESTAMP COMMENT 'ngày tạo đơn cut off',
    action STRING COMMENT 'thao tác (chi tiết hơn trạng thái)',
    soc_id STRING COMMENT 'mã cước',
    finish_date TIMESTAMP COMMENT '',
    legacy BOOLEAN COMMENT 'có phải hệ thống cũ',
    tag STRING COMMENT 'nhãn',
    pickup_time TIMESTAMP COMMENT 'thời gian hẹn lấy',
    warehouse_log STRING COMMENT 'log thay đổi kho',
    is_partial_return BOOLEAN COMMENT 'đơn giao trả 1 phần',
    items STRING COMMENT 'items chi tiết trong đơn',
    pick_shift STRING COMMENT 'ca lấy',
    deliver_shift STRING COMMENT 'ca giao',
    return_shift STRING COMMENT 'ca trả hàng',
    sort_code STRING COMMENT 'mã phân loại',
    first_picked_time TIMESTAMP COMMENT 'thời gian lấy đầu tiên',
    lost_time TIMESTAMP COMMENT 'thời gian mất hàng',
    num_pick INTEGER COMMENT 'số lần lấy',
    num_deliver INTEGER COMMENT 'số lần giao',
    num_return INTEGER COMMENT 'số lần trả',
    pick_user INTEGER COMMENT 'nhân viên lấy Driver',
    deliver_user INTEGER COMMENT 'mã nhân viên giao hàng Driver',
    return_user INTEGER COMMENT 'nhân viên trả Driver',
    lost_user INTEGER COMMENT 'người xác nhận mất hàng',
    end_pick_time TIMESTAMP COMMENT 'thời gian kết thúc lấy',
    first_delivered_time TIMESTAMP COMMENT 'thời gian giao hàng đầu tiên',
    return_time TIMESTAMP COMMENT 'thời gian hẹn trả',
    s2r_time TIMESTAMP COMMENT 'thời gian bắt đầu tính để chờ chuyển trả hàng',
    end_delivery_time TIMESTAMP COMMENT 'thời gian kết thúc giao',
    end_return_time TIMESTAMP COMMENT 'thời gian kết thúc trả',
    end_success_time TIMESTAMP COMMENT 'thời gian hoàn tất đơn hàng (GTTC)',
    updated_warehouse INTEGER COMMENT 'mã kho cập nhất',
    current_transport_warehouse_id INTEGER COMMENT 'mã kho hiện tại đang luân chuyển đến',
    internal_process STRING COMMENT '',
    table_partition STRING COMMENT '',
    extra_service STRING COMMENT 'dịch vụ bổ sung',
    cod_failed_amount INTEGER COMMENT 'tiền giao thất bại thu khách',
    cod_failed_collect_date TIMESTAMP COMMENT 'ngày thu tiền giao thất bại của khách',
    pods STRING COMMENT 'chứng từ giao nhận',
    discount_log STRING COMMENT '',
    is_b2b BOOLEAN COMMENT 'đơn B2B',
    cod_transferred_histories STRING COMMENT '',
    is_cod_collected BOOLEAN COMMENT 'đơn có thu cod không',
    process_by_partner BOOLEAN COMMENT 'đơn hàng do đối tác xử lí',
    process_partner_name STRING COMMENT 'tên đối tác xử lý',
    operation_partner STRING COMMENT 'đối tác vận hành',
    type_order STRING COMMENT 'loại đơn hàng (phân biệt đơn freight) (Freight hoặc Null)',
    type_order_code STRING COMMENT 'mã loại đơn hàng (phân biệt các nhóm đơn freight)',
    cod_amount_bk INTEGER COMMENT 'Số tiền COD bản ghi cũ (backup)',
    ecom_config_fee_id INTEGER COMMENT 'ID cấu hình phí thương mại điện tử',
    ecom_extra_cost_id INTEGER COMMENT 'ID chi phí bổ sung thương mại điện tử',
    config_fee_id INTEGER COMMENT 'ID cấu hình phí',
    extra_cost_id INTEGER COMMENT 'ID chi phí bổ sung',
    config_fee_id_new STRING COMMENT 'ID cấu hình phí mới (chuẩn hóa)',
    extra_cost_id_new STRING COMMENT 'ID chi phí bổ sung mới (chuẩn hóa)',
    is_new_multiple BOOLEAN COMMENT 'Cờ cho biết đơn hàng nhiều gói (phiên bản mới)',
    order_code_hash STRING COMMENT 'Giá trị băm của mã đơn hàng (ẩn danh hóa)',
    client_id_hash INTEGER COMMENT 'Giá trị băm của mã khách hàng (ẩn danh hóa)',
    shop_id_hash INTEGER COMMENT 'Giá trị băm của mã shop (ẩn danh hóa)',
    updated_client_hash INTEGER COMMENT 'Giá trị băm của client khi cập nhật',
    created_client_hash INTEGER COMMENT 'Giá trị băm của client khi tạo'
);
"""

# --- Define the static DDL schema string for dim_location ---
DIM_LOCATION_SCHEMA_DDL = """
CREATE TABLE dim_location (
    ward_id STRING COMMENT 'Mã phường/xã',
    ward_name STRING COMMENT 'Tên phường/xã',
    ward_status INTEGER COMMENT 'Trạng thái phường/xã (0 = ngưng, 1 = hoạt động)',
    district_id INTEGER COMMENT 'ID quận/huyện',
    district_code STRING COMMENT 'Mã quận/huyện',
    district_name STRING COMMENT 'Tên quận/huyện',
    district_type STRING COMMENT 'Loại quận/huyện (Nội Thành/Ngoại Thành 1/Ngoại Thành 2)',
    province_id INTEGER COMMENT 'ID tỉnh/thành phố',
    province_name STRING COMMENT 'Tên tỉnh/thành phố',
    region_id INTEGER COMMENT 'ID khu vực',
    region_name STRING COMMENT 'Tên khu vực',
    region_fullname STRING COMMENT 'Tên vùng đầy đủ',
    region_shortname STRING COMMENT 'Tên vùng rút gọn',
    region_code_hrw STRING COMMENT 'Mã vùng HRW'
);
"""

# --- Define the static DDL schema string for dim_warehouse ---
DIM_WAREHOUSE_SCHEMA_DDL = """
CREATE TABLE dim_warehouse (
    warehouse_id INTEGER COMMENT 'Mã kho',
    department_id INTEGER COMMENT 'Mã phòng ban',
    warehouse_name STRING COMMENT 'Tên kho',
    warehouse_address STRING COMMENT 'Địa chỉ kho',
    is_enabled BOOLEAN COMMENT 'Trạng thái hoạt động (true/false)',
    status_hrw INTEGER COMMENT 'Trạng thái hoạt động trên hệ thống HRW (1 đang hoạt động, 0 ngưng)',
    warehouse_type STRING COMMENT 'Loại kho (BC bưu cục, KTC kho trung chuyển, KHL kho khách)',
    ward_code STRING COMMENT 'Mã phường/xã',
    ward_name STRING COMMENT 'Tên phường/xã',
    district_id INTEGER COMMENT 'Mã quận/huyện',
    district_name STRING COMMENT 'Tên quận/huyện',
    province_id INTEGER COMMENT 'Mã tỉnh/thành phố',
    province_name STRING COMMENT 'Tên tỉnh/thành phố',
    region_shortname STRING COMMENT 'Tên vùng rút gọn',
    region_fullname STRING COMMENT 'Tên vùng đầy đủ',
    team_name STRING COMMENT 'Tên team HRW phụ trách',
    section_name STRING COMMENT 'Tên section HRW phụ trách',
    department_name STRING COMMENT 'Tên phòng ban HRW phụ trách',
    gdv_id INTEGER COMMENT 'Mã Giám đốc vùng',
    gdv_name STRING COMMENT 'Tên Giám đốc vùng',
    pgdv_id STRING COMMENT 'Mã Phó Giám đốc vùng',
    pgdv_name STRING COMMENT 'Tên Phó Giám đốc vùng',
    area_manager_id INTEGER COMMENT 'Mã Area Manager phụ trách',
    area_manager_name STRING COMMENT 'Tên Area Manager phụ trách',
    station_leader_id INTEGER COMMENT 'Mã Trưởng bưu cục',
    station_leader_name STRING COMMENT 'Tên Trưởng bưu cục',
    latitude FLOAT64 COMMENT 'Vĩ độ kho',
    longitude FLOAT64 COMMENT 'Kinh độ kho',
    owner_location_id FLOAT64 COMMENT 'Mã kho chủ (kho ảo thuộc kho chủ này)',
    is_virtual BOOLEAN COMMENT 'true kho ảo, false kho vật lý',
    created_time TIMESTAMP COMMENT 'Thời gian tạo kho',
    last_updated_time TIMESTAMP COMMENT 'Thời gian cập nhật cuối',
    hrw_updated_at TIMESTAMP COMMENT 'Thời gian cập nhật cuối trên HRW'
);
"""

# --- Define the static DDL schema string for middle_mile_log ---
MIDDLE_MILE_LOG_SCHEMA_DDL = """
CREATE TABLE middle_mile_log (
    action_type STRING COMMENT 'Tên thao tác (must have when query into this table)',
    order_code_hash STRING COMMENT 'Mã đơn hàng (băm ẩn danh)',
    package_code_hash STRING COMMENT 'Mã kiện hàng (băm ẩn danh)',
    action_date DATE COMMENT 'Ngày thao tác',
    action_time STRING COMMENT 'Giờ thao tác',
    warehouse_id INTEGER COMMENT 'Mã kho/bưu cục thực hiện thao tác'
);
"""

# --- Define the static DDL schema string for revenue_order ---
REVENUE_ORDER_SCHEMA_DDL = """
CREATE TABLE revenue_order (
    order_code_hash STRING,
    rev FLOAT64
);
"""
# --- Define the static DDL schema string for sla_delivery ---
SLA_DELIVERY_SCHEMA_DDL = """
CREATE TABLE sla_delivery (
    route STRING COMMENT 'Phân loại tuyến',
    from_district STRING COMMENT 'Tên quận/huyện lấy',
    to_district STRING COMMENT 'Tên quận/huyện giao',
    from_district_id INTEGER COMMENT 'Mã định danh quận/huyện lấy',
    to_district_id INTEGER COMMENT 'Mã định danh quận/huyện giao',
    delivery_sla INTEGER COMMENT 'Quy định SLA‒số ngày giao'
);
"""

# --- Define the static, efficient format for the abbreviations ---
ABBREVIATIONS_AND_JARGON_LIST = """
Here is a list of company-specific terms, abbreviations, and jargon:

**Customer & Sales Terms:**
- Key Account (KA): Khách hàng lớn (Large Customer)
- Small Medium Enterprise (SME): Khách hàng vừa và nhỏ (Small and Medium-sized Customer)
- Khách Hàng Mới (KHM): KH lần đầu hoặc quay lại sau 90 ngày (New customer or returning after 90 days)
- Khách Hàng Cũ (KHC): KH đang sử dụng dịch vụ (Existing customer)
- Phân loại A,B,C,D,E,F: Phân loại KH theo doanh thu (Customer classification by revenue)
- Shop Siêu Sao: Chương trình khách hàng thân thiết (Loyalty program for customers)
- Dự án 7K (7K): Dự án Toàn dân bán hàng (Project "Everyone Sells")

**Employee & Role Terms:**
- Nhân viên Phát triển Thị trường (NVPTTT): Nhân viên giao nhận (Delivery staff/shipper)
- Chiến Binh Siêu Sao (CBSS): NVPTTT có doanh thu KHM ≥ 1 triệu/tháng (A shipper with new customer revenue >= 1M VND/month)
- Đại Hiệp: CBSS liên tục 3 tháng (CBSS for 3 consecutive months)
- Cao Thủ: CBSS liên tục 6 tháng (CBSS for 6 consecutive months)
- Đại Cao Thủ: CBSS liên tục 9 tháng (CBSS for 9 consecutive months)
- Chiến Thần: CBSS liên tục 12 tháng (CBSS for 12 consecutive months)
- NVPTTT siêu giao: NV có > 70 % thu nhập từ giao (Shipper with >70% income from delivering)
- NVPTTT siêu lấy: (No explanation provided)
- Nhân viên xử lý (NVXL): Nhân viên xử lý đơn trong kho (Warehouse processing staff)

**Management & Department Terms:**
- Ban Dự Án (BDA): Nhóm triển khai dự án (Project Team)
- Area Manager (AM): Quản lý khu vực (Area Manager)
- Trưởng Bưu Cục (TBC): Quản lý bưu cục (Post Office/Station Leader)
- Giám đốc Vùng (GĐV): Giám đốc vùng (Regional Director)
- Human Resources Business Partner (HRBP): Đối tác nhân sự
- Compensation & Benefits (CnB): Phòng Tiền lương & Phúc lợi (Payroll & Benefits Department)
- Business Intelligence (BI): Phòng Phân tích dữ liệu (Data Analysis Department)
- Finance (FIN): Phòng Tài chính (Finance Department)
- Operational Excellence (OE): Phòng Chiến lược Vận hành (Operational Strategy Department)

**Geographic Regions:**
- Đông Bắc Bộ (DBB): Vùng địa lý (Northeast region)
- Bắc Trung Bộ (BTB): Vùng địa lý (North Central Coast region)
- Tây Bắc Bộ (TBB): Vùng địa lý (Northwest region)
- Duyên hải (DSH): Vùng địa lý (Coastal region)
- Đông Nam Bộ (DNB): Vùng địa lý (Southeast region)
- Nam Trung Bộ (NTB): Vùng địa lý (South Central Coast region)
- Tây Nam Bộ (TNB): Vùng địa lý (Southwest/Mekong Delta region)
- Hồ Chí Minh (HCM): Vùng địa lý
- Hà Nội (HNO): Vùng địa lý

**Operational & Process Terms:**
- Giao Thành Công (GTC): Trạng thái giao hàng thành công (Successful Delivery status)
- Lấy Thành Công (LTC): Trạng thái lấy hàng thành công (Successful Pickup status)
- Giao Thất Bại - Thu tiền (GTB-TT): Giao không thành công lần thứ 3 - thu tiền (Failed delivery attempt 3 - collect fee)
- Stop: Đơn vị quy đổi (1 Stop = 4 kg) (Unit of conversion)
- Giao-Lấy Hỗn Hợp (GLHH): Mô hình giao lấy kết hợp (Combined delivery and pickup model)
- Kho Khách Hàng Lớn (KHL): Mô hình kho riêng cho KH lớn (Dedicated warehouse model for large customers)
- Bưu cục Hybrid: BC kết hợp nhiều tuyến (Hybrid post office combining multiple routes)
- Giao Ca 2: Mô hình giao 2 ca/ngày (2-shift delivery model)
- Chia tuyến: Phân chia địa bàn hoạt động (Route planning/zoning)
- “Cứu bể”: Giải pháp khắc phục BC bất ổn (Solution to fix an unstable post office)
- Standard Operating Procedure (SOP): Quy trình chuẩn
- Quy hoạch bưu cục: Kế hoạch tổ chức BC (Post office organization planning)

**HR & Payroll Terms:**
- Lương Hoa Hồng: Cách tính lương theo % doanh thu (Commission-based salary)
- Lương Đơn Hàng: Cách tính lương cũ theo khối lượng (Old salary model based on volume)
- Auto-payroll: Hệ thống tính lương tự động (Automated payroll system)
- Payslip: Bảng lương chi tiết
- Kỳ lương: Chu kỳ trả lương (2 kỳ/tháng) (Payroll period, twice a month)

**System & Technology Terms:**
- Electronic Know Your Customer (eKYC): Xác minh khách hàng điện tử
- Talent Management System: Hệ thống quản trị nhân tài
- Bảng xếp hạng vùng: Xếp hạng hiệu quả các vùng (Regional performance leaderboard)
"""

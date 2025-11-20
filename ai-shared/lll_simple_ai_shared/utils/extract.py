MODALITY_TYPES = {
    "asr": "语音",  # 语音识别输入
    "tts": "语音",  # 语音输出
    "text": "文本",
    "motor": "动作",
    "vision": "图像",
}


def modality_type_to_name(type):
    return MODALITY_TYPES.get(type, "未知")


def event_entity_to_name(understood_data):
    if not understood_data:
        return "未知"

    event_entity = understood_data.get("event_entity", None)

    if event_entity == "me":
        return "你"
    elif event_entity is None:
        return "未知"

    return event_entity


def understood_data_get_main_content(understood_data):
    if not understood_data:
        return "未知"

    main_content = understood_data.get("main_content", None)
    if main_content is None:
        return "未知"

    return main_content


def safe_event_to_string(event):
    try:
        # 检查understood_data
        understood_data = event.get("understood_data", None)
        if understood_data is None:
            return None

        modality_type = event.get("modality_type", None)
        if modality_type is None:
            modality_type = "未知"
        else:
            modality_type = MODALITY_TYPES.get(modality_type, "未知")

        # 获取event_entity
        event_entity = understood_data.get("event_entity", None)
        if event_entity == "me":
            event_entity = "你"
        elif (
            event_entity is None
            or not isinstance(event_entity, str)
            or not event_entity.strip()
        ):
            event_entity = "未知"
        else:
            event_entity = event_entity.strip()

        # 获取main_content
        main_content = understood_data.get("main_content", None)
        if (
            main_content is None
            or not isinstance(main_content, str)
            or not main_content.strip()
        ):
            main_content = "未知"
        else:
            main_content = main_content.strip()

        return f"类型: {modality_type} | 角色: {event_entity} | 内容: {main_content}"

    except Exception as e:
        print(e)
        return None


def extract_events_string(recent_events):
    if recent_events is None:
        return "无"
    if not recent_events:
        return "无"

    valid_strings = []
    for event in recent_events:
        # 跳过None事件
        if event is None:
            continue

        event_str = safe_event_to_string(event)
        if event_str:
            valid_strings.append(event_str)

    return "- " + "\n- ".join(valid_strings) if valid_strings else "无"


def default_extract_strings(data_list, field=None):
    """从对象列表中提取字符串"""
    if not data_list:
        return "无"

    strings = []
    for item in data_list:
        if field and hasattr(item, field):
            # 对象字段提取
            value = getattr(item, field, "")
        elif field and isinstance(item, dict):
            # 字典字段提取
            value = item.get(field, "")
        else:
            # 直接使用字符串
            value = str(item)

        if value and value not in strings:
            strings.append(str(value))

    return "- " + "\n- ".join(strings) if strings else "无"


def default_extract_fields_to_string(
    data_list, field_configs, list_name="无", separator=" | "
):
    """
    通用方法：从List[Dict]中提取字段并格式化为字符串

    Args:
        data_list: 数据列表，每个元素是字典
        field_configs: 字段配置列表，每个配置是字典，包含：
            - key: 数据中的字段名
            - display: 显示的名称
            - default: 默认值（可选）
            - processor: 值处理函数（可选）
            - format_template: 字段格式化模板（可选），支持占位符：
                {display}: 显示名称
                {value}: 字段值
                {key}: 原始字段名
                默认值为 "{display}: {value}"
        list_name: 列表名称，当数据为空时返回这个值
        separator: 字段之间的分隔符，默认为 " | "

    Returns:
        格式化后的字符串
    """
    if not data_list:
        return list_name

    result_lines = []

    for item in data_list:
        if item is None:
            continue

        field_pairs = []
        for config in field_configs:
            field_key = config["key"]
            display_name = config["display"]
            default_value = config.get("default", "未知")
            processor = config.get("processor")
            format_template = config.get("format_template", "{display}: {value}")

            # 获取值
            value = item.get(field_key)

            # 处理空值
            if value is None:
                value = default_value
            elif isinstance(value, str) and not value.strip():
                value = default_value

            # 应用处理器
            if processor and callable(processor):
                try:
                    value = processor(value)
                except Exception:
                    value = default_value

            # 格式化字段显示
            formatted_field = format_template.format(
                display=display_name, value=value, key=field_key
            )
            field_pairs.append(formatted_field)

        if field_pairs:
            result_lines.append("- " + separator.join(field_pairs))

    return "\n".join(result_lines) if result_lines else list_name

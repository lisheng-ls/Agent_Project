from app.entities.metric_info import MetricInfo
from app.models.metric_info import MetricInfoMySQL


class MetricInfo:
    #将orm实体类转换为业务实体类，用于输出数据

    @staticmethod
    def to_entity(metric_info_mysql:MetricInfoMySQL) -> MetricInfo:
        # 归一化处理relevant_columns
        if  isinstance (metric_info_mysql.relevant_columns,list):
            relevant_columns = metric_info_mysql.relevant_columns
        else:
            relevant_columns = []

        # 归一化处理alias
        if  isinstance (metric_info_mysql.alias,list):
            alias = metric_info_mysql.alias
        else:
            alias = []
        return  MetricInfo(
            id = metric_info_mysql.id,
            name = metric_info_mysql.name,
            description= metric_info_mysql.description,
            relevant_columns = relevant_columns,
            alias =alias
        )

    #将业务实体类转换为orm实体类，用户存储数据
    @staticmethod
    def to_model(metric_info: MetricInfo)-> MetricInfoMySQL :
        return MetricInfoMySQL(
            id = metric_info.id,
            name = metric_info.name,
            description= metric_info.description,
            relevant_columns = metric_info,
            alias =metric_info
        )
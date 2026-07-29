from app.entities.column_metric import ColumnMetric
from app.models.column_metric import ColumnMetricMySQL


class ColumnMetricMapper:
    #将orm实体类转换为业务实体类，用于输出数据
    @staticmethod
    def to_entity(column_metric_mysql:ColumnMetricMySQL) -> ColumnMetric:
        return  ColumnMetric(
            column_id=column_metric_mysql.column_id,
            metric_id=column_metric_mysql.metric_id,
        )

    #将业务实体类转换为orm实体类，用户存储数据
    @staticmethod
    def to_model(column_metric : ColumnMetric)-> ColumnMetricMySQL :
        return ColumnMetricMySQL(
            column_id=column_metric.column_id,
            metric_id=column_metric.metric_id,
        )

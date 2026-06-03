# Redis 与中间件学习笔记

Redis 内存数据库及常见中间件学习与实践。

## 📚 Redis 学习内容

- Redis 基础数据结构（String、Hash、List、Set、ZSet、Stream、Bitmap、HyperLogLog）
- 持久化机制（RDB、AOF、混合持久化）
- 缓存策略与设计模式（Cache Aside、Write Through、Write Behind）
- 分布式锁实现（SET NX EX、Redisson、Redlock）
- 发布订阅机制（Pub/Sub、Stream）
- 集群部署与高可用（主从复制、哨兵、Cluster）
- 性能优化与监控
- 常见应用场景（缓存、会话、排行榜、限流、消息队列）

## 🔧 中间件知识概览

| 类型 | 中间件 | 典型场景 |
|------|--------|----------|
| 缓存 | Redis、Memcached | 热点数据缓存、会话存储 |
| 消息队列 | Kafka、RabbitMQ、RocketMQ | 异步解耦、削峰填谷、事件驱动 |
| 搜索引擎 | Elasticsearch | 全文检索、日志分析 |
| 配置中心 | Nacos、Apollo | 动态配置、服务发现 |
| 分布式协调 | ZooKeeper、etcd | 分布式锁、选主、配置管理 |

详见 [中间件知识概览](./middleware_overview.md)

## 📝 笔记结构

- [Redis 基础知识](./redis_basics.md) - 数据结构、持久化、集群等详解
- [中间件知识概览](./middleware_overview.md) - Redis、Kafka、RabbitMQ 等中间件对比与选型
- 实践案例和代码示例
- 性能调优经验
- 最佳实践总结

## 🔗 相关资源

- [Redis 官方文档](https://redis.io/docs/)
- [Kafka 官方文档](https://kafka.apache.org/documentation/)
- [RabbitMQ 官方文档](https://www.rabbitmq.com/documentation.html)
- 持续更新中...


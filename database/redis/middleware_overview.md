# 中间件知识概览

## 1. 缓存类中间件

### Redis vs Memcached

| 对比项 | Redis | Memcached |
|--------|-------|-----------|
| 数据结构 | 丰富（String/Hash/List/Set/ZSet/Stream 等） | 仅 Key-Value |
| 持久化 | 支持 RDB、AOF | 不支持 |
| 主从/集群 | 支持 | 不支持（多实例需客户端分片） |
| 单线程 | 是（6.0 后多线程 IO） | 多线程 |
| 适用场景 | 缓存、会话、消息队列、排行榜等 | 纯 KV 缓存，高并发读 |

**选型建议**：需要丰富数据结构或持久化选 Redis；纯缓存且 QPS 极高可考虑 Memcached。

---

## 2. 消息队列中间件

### Kafka vs RabbitMQ vs RocketMQ

| 对比项 | Kafka | RabbitMQ | RocketMQ |
|--------|-------|----------|----------|
| 吞吐量 | 百万级/秒 | 万级/秒 | 十万级/秒 |
| 延迟 | 毫秒级 | 微秒级 | 毫秒级 |
| 消息顺序 | 分区内有序 | 单队列有序 | 队列内有序 |
| 消息回溯 | 支持（按 offset） | 不支持 | 支持 |
| 协议 | 自有协议 | AMQP | 自有协议 |
| 典型场景 | 日志、大数据、流处理 | 业务消息、复杂路由 | 电商、金融、订单 |

### 核心概念对比

**Kafka**
- Topic、Partition、Consumer Group、Offset
- 持久化到磁盘，支持高吞吐
- 适合日志采集、流式计算、事件溯源

**RabbitMQ**
- Exchange、Queue、Binding、Routing Key
- 支持多种交换类型：Direct、Topic、Fanout、Headers
- 适合复杂路由、事务消息、延迟队列

**RocketMQ**
- Topic、Queue、Tag、Consumer Group
- 支持事务消息、延迟消息、顺序消息
- 阿里系，中文文档完善

---

## 3. 搜索引擎

### Elasticsearch

- 基于 Lucene 的分布式搜索引擎
- 倒排索引、全文检索、聚合分析
- 典型场景：日志分析（ELK）、商品搜索、监控指标

---

## 4. 配置中心与服务发现

### Nacos vs Apollo

| 对比项 | Nacos | Apollo |
|--------|-------|--------|
| 配置管理 | 支持 | 支持（更细粒度） |
| 服务发现 | 支持 | 不支持 |
| 多环境 | 支持 | 支持（环境隔离更清晰） |
| 灰度发布 | 支持 | 支持 |
| 生态 | 阿里云、Spring Cloud Alibaba | 携程开源 |

---

## 5. 分布式协调

### ZooKeeper vs etcd

| 对比项 | ZooKeeper | etcd |
|--------|-----------|------|
| 协议 | ZAB | Raft |
| 接口 | 自定义 API | RESTful + gRPC |
| 典型场景 | Kafka、Hadoop、Dubbo | Kubernetes、服务发现 |
| 性能 | 读多写少 | 读写均衡 |

**核心能力**：分布式锁、选主、配置管理、服务注册与发现

---

## 6. 中间件选型速查

| 需求 | 推荐 |
|------|------|
| 热点数据缓存 | Redis |
| 会话共享 | Redis |
| 排行榜/计数器 | Redis |
| 分布式锁 | Redis / ZooKeeper / etcd |
| 日志/大数据流 | Kafka |
| 业务消息、复杂路由 | RabbitMQ |
| 电商订单、事务消息 | RocketMQ |
| 全文检索、日志分析 | Elasticsearch |
| 服务发现 + 配置 | Nacos |
| K8s 生态 | etcd |

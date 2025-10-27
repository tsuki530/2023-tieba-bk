<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Django 百度百科风格社区系统项目文档</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
            font-weight: 300;
        }
        
        section {
            background: white;
            margin: 25px 0;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        section:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        h2 {
            color: #2c3e50;
            border-left: 5px solid #3498db;
            padding-left: 15px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        h3 {
            color: #34495e;
            margin: 20px 0 15px 0;
            font-size: 1.4em;
        }
        
        h4 {
            color: #7f8c8d;
            margin: 15px 0 10px 0;
            font-size: 1.2em;
        }
        
        .goal-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .goal-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }
        
        .architecture {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }
        
        .tech-stack {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .tech-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .tech-item:hover {
            background: #3498db;
            color: white;
            transform: scale(1.05);
        }
        
        .mind-map {
            background: #2c3e50;
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            line-height: 1.8;
        }
        
        .highlight {
            background: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
        }
        
        .code-block {
            background: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }
        
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }
        
        .summary-card h4 {
            color: white;
            margin-bottom: 15px;
        }
        
        footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #7f8c8d;
            border-top: 1px solid #bdc3c7;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            section {
                padding: 20px;
                margin: 15px 0;
            }
            
            h1 {
                font-size: 2em;
            }
            
            .goal-grid, .tech-stack, .summary-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Django 百度百科风格社区系统项目文档</h1>
            <div class="subtitle">知识管理与社区互动一体化平台</div>
        </header>

        <section id="overview">
            <h2>项目概述</h2>
            
            <h3>项目背景</h3>
            <p>当前百科类平台普遍存在<strong>内容更新滞后</strong>、<strong>用户互动性差</strong>、<strong>社区氛围薄弱</strong>等问题。传统百科以单向信息传递为主，缺乏用户间的深度交流和实时互动，无法满足现代用户对知识获取和社交讨论的双重需求。</p>
            
            <h3>项目目标</h3>
            <div class="goal-grid">
                <div class="goal-card">
                    <h4>核心功能目标</h4>
                    <ul>
                        <li>构建功能完善的百科社区系统</li>
                        <li>实现用户注册、登录、词条编辑、帖子互动等核心功能</li>
                        <li>建立完整的用户权限和内容管理体系</li>
                        <li>集成搜索、消息、社交等增强功能模块</li>
                    </ul>
                </div>
                
                <div class="goal-card">
                    <h4>用户体验目标</h4>
                    <ul>
                        <li>提供优质的用户体验和界面设计</li>
                        <li>采用现代化的前端技术栈，确保界面美观易用</li>
                        <li>实现响应式设计，支持多终端访问</li>
                        <li>优化交互流程，降低用户使用门槛</li>
                    </ul>
                </div>
                
                <div class="goal-card">
                    <h4>系统质量目标</h4>
                    <ul>
                        <li>确保系统的稳定性和安全性</li>
                        <li>建立健壮的后端架构，保证服务高可用性</li>
                        <li>实施严格的数据安全保护和权限控制</li>
                        <li>采用性能优化策略，提升系统响应速度</li>
                    </ul>
                </div>
                
                <div class="goal-card">
                    <h4>社区生态目标</h4>
                    <ul>
                        <li>打造活跃的知识分享社区生态</li>
                        <li>通过激励机制促进用户内容贡献</li>
                        <li>构建良性的用户互动和交流环境</li>
                        <li>形成知识创造与社区互动的正向循环</li>
                    </ul>
                </div>
            </div>
        </section>

        <section id="architecture">
            <h2>系统架构设计</h2>
            
            <h3>整体架构</h3>
            <div class="architecture">
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   前端层         │    │     API网关层     │    │    服务层        │
│                 │    │                  │    │                 │
│ ● Vue.js 3      │───▶│ ● Nginx         │───▶│ ● Django       │
│ ● Element Plus  │    │ ● 负载均衡       │    │ ● DRF          │
│ ● Veaury        │    │ ● 路由转发       │    │ ● Channels     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   数据层         │    │    缓存层         │    │   外部服务       │
│                 │    │                  │    │                 │
│ ● PostgreSQL   │    │ ● Redis         │    │ ● 阿里云OSS     │
│ ● Elasticsearch│    │ ● Memcached     │    │ ● 微信登录       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
            </div>
            
            <h3>微服务模块划分</h3>
            <div class="tech-stack">
                <div class="tech-item">用户服务：认证、权限、个人资料</div>
                <div class="tech-item">内容服务：词条管理、帖子管理</div>
                <div class="tech-item">搜索服务：全文检索、智能推荐</div>
                <div class="tech-item">消息服务：实时通知、私信聊天</div>
                <div class="tech-item">文件服务：图片上传、文件存储</div>
            </div>
        </section>

        <section id="prototype">
            <h2>产品原型设计</h2>
            
            <h3>页面结构规划</h3>
            <div class="architecture">
首页
├── 导航栏 (Logo、搜索框、用户菜单)
├── 主内容区
│   ├── 轮播图 (热门词条)
│   ├── 分类导航
│   ├── 最新词条
│   └── 热门讨论
└── 页脚 (站点信息)

词条详情页
├── 面包屑导航
├── 词条标题区
├── 词条内容区
├── 词条信息 (作者、时间、浏览量)
└── 互动区 (点赞、收藏、评论)

个人中心
├── 用户信息卡片
├── 我的词条
├── 我的帖子
├── 我的收藏
└── 消息中心
            </div>
            
            <h3>交互设计原则</h3>
            <div class="tech-stack">
                <div class="tech-item">一致性：统一的视觉风格和交互模式</div>
                <div class="tech-item">反馈性：及时的操作反馈和状态提示</div>
                <div class="tech-item">简洁性：减少不必要的操作步骤</div>
                <div class="tech-item">可访问性：支持键盘操作和屏幕阅读器</div>
            </div>
        </section>

        <section id="implementation">
            <h2>项目技术实现方案</h2>
            
            <h3>后端技术栈详述</h3>
            
            <h4>Django 配置优化</h4>
            <div class="code-block">
# settings.py 关键配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wiki_community',
        'CONN_MAX_AGE': 600,  # 连接池
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
            </div>
            
            <h4>API 设计规范</h4>
            <div class="tech-stack">
                <div class="tech-item">RESTful 接口设计</div>
                <div class="tech-item">JWT 身份认证</div>
                <div class="tech-item">接口版本管理</div>
                <div class="tech-item">限流和防刷机制</div>
            </div>
        </section>

        <section id="veaury">
            <h2>Veaury 技术架构实现</h2>
            
            <h3>混合开发架构</h3>
            <div class="architecture">
┌─────────────────────────────────────────────────┐
│                 前端应用层                        │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐               │
│  │   Vue组件   │  │  React组件  │               │
│  │             │  │             │               │
│  │ ● 词条编辑  │  │ ● 实时聊天  │               │
│  │ ● 个人中心  │  │ ● 消息通知  │               │
│  └─────────────┘  └─────────────┘               │
│          │                     │                │
│          └─────────┐ ┌─────────┘                │
│                    │ │                          │
│  ┌─────────────────▼─▼──────────────────┐       │
│  │           Veaury 整合层               │       │
│  │                                      │       │
│  │ ● Vue/React 组件互调                 │       │
│  │ ● 统一状态管理                       │       │
│  │ ● 共享工具函数                       │       │
│  └─────────────────┬──────────────────┘       │
│                    │                          │
└────────────────────┼──────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│                后端服务层                         │
│                                                 │
│ ● Django REST API                              │
│ ● WebSocket 实时服务                           │
│ ● 数据库操作                                    │
└─────────────────────────────────────────────────┘
            </div>
            
            <h3>Veaury 配置示例</h3>
            <div class="code-block">
// veaury 配置
import { createApp } from 'vue'
import { applyPureReactInVue } from 'veaury'

// Vue 中使用 React 组件
const ReactComponentInVue = applyPureReactInVue(ReactComponent)

// 主应用配置
createApp({
  components: {
    ReactComponentInVue
  }
})
            </div>
        </section>

        <section id="mindmap">
            <h2>项目脑图</h2>
            <div class="mind-map">
百科社区系统
├── 用户系统
│   ├── 注册登录
│   │   ├── 邮箱注册
│   │   ├── 手机注册
│   │   └── 第三方登录
│   ├── 个人中心
│   │   ├── 资料编辑
│   │   ├── 头像管理
│   │   └── 隐私设置
│   └── 社交关系
│       ├── 关注系统
│       ├── 粉丝列表
│       └── 用户主页
│
├── 内容系统
│   ├── 词条管理
│   │   ├── 创建词条
│   │   ├── 编辑历史
│   │   ├── 版本对比
│   │   └── 词条分类
│   ├── 帖子系统
│   │   ├── 发布帖子
│   │   ├── 回复评论
│   │   ├── 点赞收藏
│   │   └── 帖子分类
│   └── 内容审核
│       ├── 审核流程
│       ├── 举报机制
│       └── 内容过滤
│
├── 搜索系统
│   ├── 全文搜索
│   ├── 高级筛选
│   ├── 搜索建议
│   └── 历史记录
│
├── 消息系统
│   ├── 系统通知
│   ├── 私信聊天
│   ├── @提及
│   └── 消息设置
│
└── 管理系统
    ├── 用户管理
    ├── 内容管理
    ├── 数据统计
    └── 系统配置
            </div>
        </section>

        <section id="summary">
            <h2>项目总结</h2>
            
            <h3>技术亮点</h3>
            <div class="summary-grid">
                <div class="summary-card">
                    <h4>架构设计</h4>
                    <p>前后端分离架构 + 微服务设计，确保系统可扩展性和维护性</p>
                </div>
                <div class="summary-card">
                    <h4>混合开发</h4>
                    <p>Veaury 实现 Vue 和 React 组件混合开发，发挥各自技术优势</p>
                </div>
                <div class="summary-card">
                    <h4>实时通信</h4>
                    <p>WebSocket 集成实现消息实时推送和在线聊天功能</p>
                </div>
                <div class="summary-card">
                    <h4>搜索优化</h4>
                    <p>Elasticsearch 全文搜索引擎，支持智能推荐和高性能检索</p>
                </div>
            </div>
            
            <h3>业务价值</h3>
            <div class="highlight">
                <p><strong>知识共享平台：</strong>为用户提供专业的知识创作和分享环境</p>
                <p><strong>社区互动生态：</strong>建立用户间的深度连接和良性互动机制</p>
                <p><strong>内容质量保障：</strong>通过审核机制和版本控制确保内容准确性</p>
                <p><strong>个性化体验：</strong>基于用户行为的智能推荐和内容分发</p>
            </div>
            
            <h3>未来规划</h3>
            <div class="tech-stack">
                <div class="tech-item">移动端开发：React Native 移动应用</div>
                <div class="tech-item">AI 功能集成：智能摘要、内容查重</div>
                <div class="tech-item">开放平台：API 接口，第三方集成</div>
                <div class="tech-item">国际化支持：多语言版本和全球化部署</div>
            </div>
        </section>

        <footer>
            <p>文档版本：v2.0 | 最后更新：2024年1月</p>
        </footer>
    </div>

    <script>
        // 添加简单的交互效果
        document.addEventListener('DOMContentLoaded', function() {
            // 为所有章节添加点击平滑滚动
            const sections = document.querySelectorAll('section');
            sections.forEach(section => {
                section.addEventListener('click', function() {
                    this.style.transform = 'scale(0.99)';
                    setTimeout(() => {
                        this.style.transform = 'scale(1)';
                    }, 150);
                });
            });
            
            // 为技术栈项添加悬停效果
            const techItems = document.querySelectorAll('.tech-item');
            techItems.forEach(item => {
                item.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-5px)';
                });
                item.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
        });
    </script>
</body>
</html>
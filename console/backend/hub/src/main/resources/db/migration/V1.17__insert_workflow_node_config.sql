INSERT INTO config_info (category, code, name, value, is_valid, remarks, create_time, update_time, order_no) VALUES('WORKFLOW_NODE_TEMPLATE', '1,2', '工具', '{
    "aliasName": "MCP",
    "idType": "mcp",
    "data":
    {
        "outputs":
        [
            {
                "id": "8ff81980-1ed7-4767-a58a-24c3023308b7",
                "name": "result",
                "schema":
                {
                    "type": "object",
                    "default": "",
                    "properties":
                    [
                        {
                            "id": "d6139baf-1e21-4138-9f69-30134a3b9ba8",
                            "name": "isError",
                            "type": "boolean",
                            "default": "",
                            "required": false,
                            "nameErrMsg": "",
                            "properties":
                            []
                        },
                        {
                            "id": "6af38267-17fe-4e77-a064-1f345035e75a",
                            "name": "content",
                            "type": "array-object",
                            "default": "",
                            "required": false,
                            "nameErrMsg": ""
                        }
                    ]
                },
                "required": false,
                "nameErrMsg": ""
            }
        ],
        "references":
        [],
        "allowInputReference": true,
        "inputs":
        [],
        "icon": "https://oss-beijing-m8.openstorage.cn/SparkBotProd/icon/common/mcp-new.png",
        "allowOutputReference": true,
        "nodeMeta":
        {
            "nodeType": "工具节点",
            "aliasName": "MCP"
        },
        "nodeParam":
        {}
    },
    "description": "快速调用符合MCP协议的工具",
    "nodeType": "mcp"
}', 1, 'MCP', '2000-01-01 00:00:00', '2025-12-15 18:58:18', 11);

UPDATE config_info SET value='[
    {
        "idType": "spark-llm",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/largeModelIcon.png",
        "name": "大模型",
        "markdown": "## 用途\\n根据输入的提示词，调用选定的大模型，对提示词作出回答\\n## 示例\\n### 输入\\n| 参数名 | 参数值 |\\n |----------------|----------------------|\\n | input（引用）| 开始-query |\\n## 提示词\\n你是一个旅行规划超级智能体，你非常善于从用户的【输入信息】中，识别出用户旅行的各种需求信息，并且整理输出。现在你的任务是，严格按照下面的定义和规则要求，仔细分析和理解下面用户的【输入信息】，输出一份用户旅行需求资料，资料包含了，【旅行目的地】、【旅行天数】、【旅行人员】、【景点偏好】、【旅行时间】\\n### 输出\\n | 变量名 | 变量值 |\\n |------------|--------|\\n | output（String）| 🌟亲爱的朋友，小助手收到啦！我已经了解到您本次旅行希望开启一段精彩的合肥三日之旅😃。请稍等片刻，我将为您生成行程卡片。在这之前，让我简短介绍一下我们这次的目的地合肥，它有着很多非常值得一去的景点。合肥的三河古镇🏯，那是一个充满古朴韵味的地方。青石板路蜿蜒曲折，两旁是白墙黑瓦的徽派建筑。当您漫步其间，仿佛穿越回了过去，能感受到岁月的沉淀和历史的韵味。还有包公园🌳，这里是为纪念包拯而建。清风阁高耸入云，站在阁顶，俯瞰整个园区，绿树成荫，湖水碧波荡漾。当您身处其中，敬仰包拯的清正廉洁，内心会感到无比的宁静和崇敬。大蜀山森林公园也是不容错过的好去处🌲，山峦起伏，绿树葱茏。沿着山间小道攀登，呼吸着清新的空气，您会感到身心都得到了极大的放松。除此之外，李鸿章故居也是非常值得一去的地方。在这里，您可以了解到李鸿章的生平事迹，感受那段波澜壮阔的历史。相信在合肥的这三天，您一定会留下美好的回忆💖。祝您旅途愉快🌟| \\n\\n![占位图片](https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-llm.png)"
    },
    {
        "idType": "ifly-code",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/codeIcon.png",
        "name": "代码",
        "markdown": "## 用途\\n面向开发者提供代码开发能力，目前仅支持python语言，允许使用该节点已定义的变量作为参数传入，返回语句用于输出函数的结果\\n## 示例\\n### 输入\\n| 参数名 | 参数值 |\\n |----------------|----------------------|\\n | location（引用）| 代码-location |\\n| person（引用）| 代码-person |\\n| day（引用）| 代码-day |\\n## 代码（将上个节点里的地名和人数引用过来，拼成地点+人数+天数+旅游攻略）\\nasync def main(args:Args)->Output: \\nparams=args.params\\n ret:Output={\\"ret\\":params[''location'']+params[''person'']+params[''day'']+''旅游攻略''}\\n return ret\\n### 输出\\n | 变量名 | 变量值 |\\n |------------|--------|\\n | ret（String）| 合肥5人3日旅游攻略| \\n\\n![占位图片](https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-code.png)"
    },
    {
        "idType": "knowledge-base",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/knowledgeIcon.png",
        "name": "知识库",
        "markdown": "## 用途\\n调用知识库，可以指定知识库进行知识检索和答复\\n## 示例\\n### 输入\\n| 参数名 | 参数值 |\\n |----------------|----------------------|\\n | Query（String）（引用）| 大模型-output |\\n## 知识库 \\n全国美食大全\\n### 输出\\n | 变量名 | 变量值 |\\n |------------|--------|\\n | OutputList（Array<Object>）| 合肥十大美食：曹操鸡、庐州烤鸭、肥东泥鳅煲、麻饼、麻花、麻糕、鸭油烧饼、肥西老母鸡、肥西肥肠煲、紫蓬山炖鹅| \\n\\n![占位图片](https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-knowledge.png)"
    },
    {
        "idType": "plugin",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/tool-icon.png",
        "name": "工具",
        "image": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-tool.png",
        "markdown": "## 用途\\n通过添加外部工具，快捷获取技能，满足用户需求\\n## 示例\\n### 输入\\n| 参数名 | 参数值 |\\n |----------------|----------------------|\\n | query（引用）【这边以bing搜索工具为例，query为该工具的必填参数】| 代码-美食-result |\\n### 输出\\n | 变量名 | 变量值 |\\n |------------|--------|\\n | result（String）| 合肥美食,合肥美食攻略,合肥美食推荐-马蜂窝庐州烤鸭店到合肥的第一天就来到了庐州烤鸭店，他家的桂花赤豆糊和鸭油烧饼还有烤鸭是很有名的，所以我就来了准备尝一尝，而且我发现有一个店有团购套餐，非常实惠哦！老乡鸡要说这个老乡鸡可以说是安徽一个代表性的连锁快餐店，而且合肥人从古就是喜欢喝鸡汤的，原名：肥西老母鸡汤，我去了点了一份小份招牌老母鸡汤，接下来为大家详细分享一下！刘鸿盛冬菇鸡饺之前做功课前以为是用冬天的蘑菇和鸡肉馅的饺子，哈哈，做完功课才发现其实就是鸡汤+馄饨+冬菇（一种蘑菇），咱们现在去合肥比较有名的老店尝一尝吧~| \\n\\n![占位图片](https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-tool.png)"
    },
    {
        "idType": "flow",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/flow-icon.png",
        "name": "工作流",
        "markdown": "## 用途\\n快速集成已发布工作流，高效复用已有能力\\n## 示例\\n### 输入\\n| 参数名 | 参数值 |\\n |----------------|----------------------|\\n | location（引用）【此参数为引入的工作流的必填参数，不可删除】| 变量提取器-location |\\n | data（引用）【此参数为引入的工作流的必填参数，不可删除】 | 变量提取器-data |  \\n### 输出\\n | 变量名 | 变量值 |\\n |------------|--------|\\n | output（String）| 合肥今天天气状况为多云，温度范围在27℃~33℃，风向风力为东北风5-6级。建议穿着透气衣物，避免长时间户外活动，注意防暑降温。具体天气情况如下：天气：多云。最高温度：33℃。最低温度：27℃。日出时间：05:23。日落时间：19:12。风向风力：东北风5-6级。相对湿度：71%。空气质量：优。| \\n\\n![占位图片](https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-flow.png)"
    },
    {
        "idType": "decision-making",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/designMakeIcon.png",
        "name": "决策",
        "markdown": "## 用途\\n大模型会根据节点输入，结合提示词内容，判断您填写的意图，决定后续的逻辑走向\\n## 示例\\n### 输入\\n| 参数名 | 参数值 |\\n |----------------|----------------------|\\n | guide（引用）| 代码-guide |\\n | food（引用） | 代码-food | \\n | hotel（引用）| 代码-hotel | \\n## 提示词\\n根据攻略{{guide}}、美食偏好{{food}}、酒店位置{{hotel}}决定走不同的意图\\n## 意图\\n意图一：旅游攻略意图描述：如果想查询旅游攻略，走该分支 意图二：美食推荐意图描述：如果想获取地方美食推荐，走该分支 意图三：酒店推荐意图描述：如果想获取酒店住宿推荐，走该分支 其他：以上分支均不满足要求，走此分支 \\n\\n![占位图片](https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-decision.png)"
    },
    {
        "idType": "if-else",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/if-else-node-icon.png",
        "name": "分支器",
        "markdown": "## 用途\\n根据设立的条件，判断选择分支走向\\n## 示例\\n### 输入\\n| 条件  | \\n |----------------|\\n  | 条件一：变量\\"开始-query\\"包含旅游或攻略（当被引用的开始节点的query变量包含旅游或攻略字样，进入这个分支） 否则：当条件不符合设定的任何条件，则进入此分支| \\n\\n![占位图片](https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-branch.jpg)"
    },
    {
        "idType": "iteration",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/iteration-icon.png",
        "name": "迭代",
        "image": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-iteration.png",
        "markdown": "## 用途\\n该节点用于处理循环逻辑，仅支持嵌套一次\\n## 示例\\n### 输入\\n| 参数名 | 参数值 |\\n |----------------|----------------------|\\n | locations（Array）| 代码-locations |\\n### 输出\\n | 变量名 | 变量值 |\\n |------------|--------|\\n | outputList（Array）| [{\\"合肥旅游攻略：\\"},{\\"南京旅游攻略：\\"},{\\"上海旅游攻略:\\"}]| \\n\\n![占位图片](https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-iteration.png)"
    },
    {
        "idType": "node-variable",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/variable-memory-icon.png",
        "name": "变量存储器",
        "image": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-var-storage.png",
        "markdown": "## 用途\\n可定义多个变量，在整个多轮会话期间持续生效，用于多轮会话期间内容保存，新建会话或者删除聊天记录后，变量将会清空\\n## 示例\\n### 输入\\n| 参数名 | 参数值 |\\n |----------------|----------------------|\\n | question| 开始-query |\\n\\n![占位图片](https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-var-storage.png)"
    },
    {
        "idType": "extractor-parameter",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/variable-extractor-icon.png",
        "name": "变量提取器",
        "image": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-var-extractor.png",
        "markdown": "## 用途\\n结合提取变量描述，将上一节点输出的自然语言进行提取\\n## 示例\\n### 输入\\n| 参数名 | 参数值 |\\n|----------------|----------------------|\\n| location | 将问题中的地点名词提取出来 |\\n| day | 将问题中的游玩天数名词提取出来 |\\n| person | 将问题中的人数名词提取出来 |\\n| data | 将问题中的日期名词提取出来 |\\n\\n![占位图片](https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-var-extractor.png)"
    },
    {
        "idType": "message",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/message-node-icon.png",
        "name": "消息",
        "image": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-message.png",
        "markdown": "## 消息\\n## 用途\\n在工作流中可以对中间过程的产物进行输出\\n## 示例\\n### 输入\\n| 参数名 | 参数值 |\\n|----------------|----------------------|\\n| result（引用）| 大模型-output |\\n| result1（引用）| 大模型-output1 |\\n### 输出\\n| 变量名 | 变量值 |\\n|------------|--------|\\n| 大模型-output| 回答内容：就您询问的问题，给您提供以下两种解决方案：方案一：{{result}}方案二：{{result1}}| \\n\\n![占位图片](https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-message.png)"
    },
    {
        "idType": "text-joiner",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/text-splicing-icon.png",
        "name": "文本拼接",
        "image": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-text-joiner.png",
        "markdown": "## 用途\\n将定义过的变量用{{变量名}}的方式引用，节点会按照拼接规则输出内容\\n## 示例\\n### 输入\\n| 参数名 | 参数值 |\\n|----------------|----------------------|\\n| age（input）| 18 |\\n| name（input）| 小明 |\\n\\n## 规则\\n我是{{name}}，今年{{age}}岁了。\\n\\n### 输出\\n| 变量名 | 变量值 |\\n|------------|--------|\\n| output（String）| 我是小明，今年18岁了。|\\n\\n![占位图片](https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/template/node-text-joiner.png)"
    },
    {
        "idType": "agent",
        "name": "Agent智能决策",
        "icon": "https://oss-beijing-m8.openstorage.cn/SparkBotProd/icon/common/agent.png",
        "markdown": "## 用途\\n该节点主要依据用户选择的策略进行工具智能调度，同时根据输入的提示词，调用选定的大模型，对提示词作出回答。\\n## 示例\\n###输入\\n| 参数名字 | 参数值 |\\n |----------------|----------------------|\\n | Input | 开始/AGENT_USER_INPUT |\\n## Agent策略\\n选择相应的策略，当前的ReAct策略可用于指导大模型完成复杂任务的结构化思考和决策过程。\\n## 工具列表\\n支持在已发布列表里同时勾选并添加多个工具或 MCP，最多添加 30 个。\\n## 自定义MCP服务器地址\\n支持自定义添加MCP服务器地址，上限3个。\\n## 提示词\\n该模块分为3个部分：\\n- **角色设定（非必填）**：让大模型按照特定的角色/输出格式进行交流的过程；\\n- **思考步骤（非必填）**：是否要干预大模型的推理过程，大模型会依据思考提示和决策策略进行调度；\\n- **用户查询/提问（query）（必填）**：用户的问题和指令，让模型知道我们想要什么。 \\n## 最大轮次\\n大模型的推理轮次，建议推理轮次大于等于工具数量，当前最大轮次为100轮，默认为10轮。\\n## 输出\\n | 参数名字 | 参数值 | 描述 |\\n |------------|--------|--------------------|\\n | Reasonging | String | 大模型思考过程 |\\n | Output | String | 大模型输出 |"
    },
    {
        "idType": "knowledge-pro-base",
        "name": "知识库pro",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/knowledgeIcon.png",
        "markdown": "## 用途\\n在复杂的场景下，通过智能策略调用知识库，可以指定知识库进行知识检索和总结回复。\\n## 回答模式\\n选择用于对问题进行拆解以及对召回结果进行总结的大模型。\\n## 策略选择\\n## Agentic RAG\\n适用于处理问题涉及多个方面，需要分解为多个子问题进行检索，例如“如何提升学生的综合素质”、可拆分成“学术成绩”、“身心健康”等多个子问题。\\n## Long RAG\\n专注于长文档内容的理解与生成，适用于长文档相关任务。\\n## 示例\\n### 输入\\n| 参数名字 | 参数值 | 描述 |\\n |----------------|----------------------|----------------------|\\n | query | String | 用户输入 |\\n## 知识库\\n选择相应的知识库，进行参数设置，用于筛选与 用户问题相似度最高的文本片段，系统同时会根据选用模型上下文窗口大小动态调整分段数量。当问题被分解时，最终汇总的片段数量为设定的top k乘以问题数。例如，一个问题分解为3个子问题，设定为召回3个片段，最终汇总3✖3=9个片段。\\n## 回答规则\\n非必填，如果有输出要求限制或对特殊情况的说明请在此补充，例如:回答用户的问题，如果没有找到答案时，请直接告诉我“不知道”。\\n### 输出\\n | 参数名字 | 参数值 | 描述 |\\n |------------|--------|--------------------|\\n | Reasonging | String | 大模型思考过程 |\\n | Output | String | 大模型输出 |\\n | result| （Array\\\\<Object\\\\>） | 召回结果"
    },
    {
        "idType": "question-answer",
        "name": "问答",
        "icon": "https://oss-beijing-m8.openstorage.cn/SparkBot/test4/answer-new2.png",
        "markdown": "## 用途\\n该节点支持中间环节向用户进行提问操作，提供预置选项提问与开放式问题提问两种方式。\\n\\n## 示例1（选项回复）\\n\\n| 参数名字 | 参数值 |\\n|-----------|--------------------------------------------------|\\n| Input     | 开始/AGENT_USER_INPUT                          |\\n| 提问内容 | 去旅游是个超棒的想法呀！能让你暂时摆脱日常的琐碎，去感受不一样的风景和文化~你目前有没有大概的方向或者想法呢？ |\\n| 回答模式 | 选项回复                                       |\\n| 设置选项内容 | A：自然风光类 B：历史文化类 C：都市繁华类 |\\n\\n### 输出\\n\\n| 参数名字 | 参数值 | 描述         |\\n|----------|--------|--------------|\\n| query    | String | 该节点提问内容 |\\n| id       | String | 用户回复选项   |\\n| content  | String | 用户回复内容   |\\n\\n---\\n\\n## 示例2（直接回复）\\n\\n| 参数名字   | 参数值                                     |\\n|------------|--------------------------------------------|\\n| Input      | 开始/AGENT_USER_INPUT                     |\\n| 提问内容   | 你想要去哪旅游？目的地类型？旅游时间？预算？ |\\n| 回答模式   | 直接回复                                   |\\n\\n### 输出\\n\\n| 参数名字 | 参数值 | 描述         |\\n|----------|--------|--------------|\\n| query    | String | 该节点提问内容 |\\n| content  | String | 用户回复内容   |\\n\\n### 参数抽取\\n\\n| 参数名字 | 参数值 | 描述       | 默认值 | 是否必要 |\\n|----------|--------|------------|--------|----------|\\n| city     | String | 地点       | --     | 是       |\\n| type     | String | 目的地类型 | --     | 是       |\\n| time     | Number | 行程时长   | --     | 是       |\\n| budget   | String | 预算       | --     | 是       |\\n"
    },
    {
        "idType": "database",
        "name": "数据库",
        "icon": "https://oss-beijing-m8.openstorage.cn/SparkBotDev/icon/user/sparkBot_1752568522509_database_icon.svg",
        "markdown": "## 用途\\n该节点可以连接指定的数据库，对数据库进行新增、查询、编辑、删除等常见操作，实现动态的数据管理。\\n\\n## 示例\\n\\n### 输入\\n\\n| 参数名字 | 参数值 |\\n|-----------|--------------------------------------------------|\\n| Input     | 开始/AGENT_USER_INPUT                          |\\n\\n### 输出\\n\\n| 参数名字 | 参数值 | 描述         |\\n|----------|--------|--------------|\\n| isSuccess    | Boolean| SQL语句执行状态标识，成功true，失败false |\\n| message       | String | 失败原因   |\\n| outputList  | （Array\\\\<Object\\\\>）| 执行结果   |\\n"
    },
    {
        "idType": "rpa",
        "name": "RPA",
        "icon": "https://oss-beijing-m8.openstorage.cn/pro-bucket/sparkBot/common/workflow/icon/knowledgeIcon.png",
        "markdown": "## 用途\\n\\nRPA（机器人流程自动化）工具节点是一个强大的自动化执行器，它通过获取RPA平台的机器人资源，直接连接并触发指定的RPA机器人流程，打通不同系统间的数据壁垒。\\n\\n## 示例\\n\\n### 输入\\n\\n| 参数名字 | 参数值 |\\n|---------|--------|\\n| inputer | 开始/AGENT_USER_INPUT |\\n\\n### 输出\\n\\n| 参数名字 | 参数值 | 描述 |\\n|---------|--------|------|\\n| outputer | String | 输出结果 |\\n\\n### 异常处理\\n\\n超时120s 重试2次 依然失败中断流程\\n\\n![占位图片](http://oss-beijing-m8.openstorage.cn/SparkBotProd/XINCHEN/rpa.PNG)"
    },
    {
        "idType": "mcp",
        "name": "MCP",
        "icon": "https://oss-beijing-m8.openstorage.cn/SparkBotProd/icon/common/mcp-new.png",
        "markdown": "## 用途\\n即插即用：通过标准化协议，为智能体无缝扩展外部工具与数据能力。\\n\\n## 示例\\n\\n调用bilibili-search MCP工具，搜索B站里的视频内容\\n\\n### 输入\\n\\n| 参数名字 | 参数值 |\\n|---------|--------|\\n| limit | 3 |\\n| page | 1 |\\n| keyword | 开始/AGENT_USER_INPUT |\\n### 输出\\n\\n| 参数名字 | 参数值 | 描述 |\\n|---------|--------|------|\\n| result | object | 输出结果 |\\n\\n### 异常处理\\n\\n超时120s 重试2次 依然失败中断流程\\n\\n![占位图片](http://oss-beijing-m8.openstorage.cn/SparkBotProd/icon/common/bilibili.jpeg)"
    }
]' WHERE category='TEMPLATE' and  code='node';


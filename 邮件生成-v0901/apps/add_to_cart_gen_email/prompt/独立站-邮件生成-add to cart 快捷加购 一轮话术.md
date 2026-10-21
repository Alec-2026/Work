# 独立站-邮件生成-add to cart 快捷加购 一轮话术

## 文档概要

- 适用节点：客户在商品详情页直接点击 Add to Cart，将商品加入购物车后尚未完成下单的主动触达。快捷加购不代表客户已有或没有稿件。
- 触达目的：以 Customer Success Manager 个人口吻，帮助客户理解商品定制选项，并根据稿件准备情况提供下一步建议。
- 模版选择：商品与行业均已知时使用模版 A；商品已知、行业未知时使用模版 B。
- 邮件结构：称呼 → 自我介绍 → 触达目的 → 商品／行业用途承接 → 基于商品属性的设计支持 → 稿件准备情况询问 → 可选  → 感谢语 → 署名。
- 个性化依据：二级行业仅用于选择候选应用场景；官网已核实的功能和商品属性用于选择 1–2 个设计支持点。客户已选属性与官网可选属性须区分，不将默认配置认定为客户选择，不将候选用途写成客户实际需求。
- CTA：询问客户是否已有准备使用的稿件，或是否需要稿件准备方面的指导；客户只需简短回复当前情况，即可获得下一步建议，不同时要求提交文件或完整规格。
- 购物车查看：不暴露加购追踪，不暗示已查看购物车或审核稿件。需要查看购物车中的具体商品及关联稿件时，先说明查看范围和目的，并征得客户同意；客户回复稿件准备情况不等于授权查看。
- 优惠规则：仅在确认客户无历史订单时加入 {{discount_script}}，保留 If 条件语气，独立放在 CTA 之后、感谢语之前，自然补充优惠信息，不催促下单或编造有效期。
- 输出要求：英文标题不超过 10 个词，正文通常不超过 150 词；最终输出包含用户信息总结、选择的模版、邮件标题、邮件正文、生成依据的合法 JSON。

## 当前节点

客户在商品详情页直接点击 Add to Cart，将商品加入购物车，之后离开，尚未完成下单。
快捷加购只能确认客户已将商品加入购物车，不能据此判断客户是否已有稿件、是否已确定定制方案，或因何离开。
触达时结合商品、已核实属性和二级行业，简短介绍可能的用途及可提供的设计支持，再询问客户是否已有准备使用的稿件，或是否需要稿件准备方面的指导。涉及查看购物车中的具体内容或关联稿件时，须先征得客户同意。

## 用户数据

- FirstName：{{first_name}}
- 快捷加购对应的商品名：{{product_name}}
- 商品配置数据: {{spec}}
- 跟进人英文名字：{{sender_first_name}}
- 跟进人完整英文署名：{{sender_name}}
- 二级行业标签：{{second_label}}

### 产品应用场景示例

- Custom Takeout Clamshell Boxes（定制外卖翻盖盒）：
  - 场景1：These boxes could be used for takeaway meals, where a restaurant name or logo may be worth highlighting.
  - 场景2：These boxes could be used for food orders at events, where an event name or short brand message may be useful.
- Custom Nonwoven Boutique Shopping Bags（定制无纺布购物袋）：
  - 场景1: These bags could be used for boutique purchases, where a store name or logo may help customers recognize the brand.
  - 场景2: These bags could be used for event giveaways, where an event name or simple brand message may be worth featuring.
- Custom Luxury Gift Box Bags（定制精品礼盒袋）：
  - 场景1: These bags could be used to present beauty products or fragrance gift sets, where a brand or collection name may be worth highlighting.
  - 场景2: These bags could be used for client gifts, where a company logo or short appreciation message may add a personal touch.
- Custom Layflat Photo Book（定制可平摊照片书）：
  - 场景1: This book could be used to collect family or travel memories, with selected photos forming the focus of each spread.
  - 场景2: This book could be used to present wedding or portrait photography, where image sequencing may help tell a cohesive story.
- Beverage Carrier Tray（饮品杯托）：
  - 场景1：These trays could be used to present drink combos, where a café name or logo may help bring the presentation together.
  - 场景2：These trays could be used for beverage service at events, where an event theme or brand message may be worth featuring.

### 产品设计支持场景示例

- Custom Takeout Clamshell Boxes（定制外卖翻盖盒）：
  - 支持1：The box dimensions and printable area provide a useful starting point for the layout. I can help you work out where to place your logo and key text.
  - 支持2：For an event name or short message, I’d be happy to suggest a layout that keeps it readable alongside your branding.
- Custom Nonwoven Boutique Shopping Bags（定制无纺布购物袋）：
  - 支持1：With single-color printing, a clear logo and simple text can work well together. I can talk you through how to prepare those elements.
  - 支持2：The bag color can influence how clearly the printed design stands out. I’d be glad to help you consider a suitable contrast.
- Custom Luxury Gift Box Bags（定制精品礼盒袋）：
  - 支持1：A brand or collection name could be the main focus of the design. From there, I can suggest how to arrange the supporting details across the exterior panels.
  - 支持2：The fold-over closure is worth considering when placing a logo or gift message. I can help you plan a position that keeps the important details visible.
- Custom Layflat Photo Book（定制可平摊照片书）：
  - 支持1：Once you have a book size and orientation in mind, I can guide you through photo cropping and text placement to suit the pages.
  - 支持2：The layflat format offers room for photos to extend across two pages. For an image you’d like to highlight, I can suggest ways to make use of that space.
- Beverage Carrier Tray（饮品杯托）：
  - 支持1：The cup openings help define where the branding can sit. I can work through placement options for your café name or logo with you.
  - 支持2：For an event theme or brand message, it helps to consider what remains visible with drinks in place. I’d be happy to suggest a layout around that.

## 设计支持逻辑

二级行业用于选择候选应用场景，商品及其已核实属性用于确定相关的设计支持方向。先简短说明可能用途，再自然承接可以提供的帮助，最后询问客户的稿件准备情况，不预设客户已有或没有稿件。

- {{use_case_sentence}}：结合商品与 {{second_label}}，生成一句简短的候选应用场景。使用 may、could 等表达，不将行业推测写成客户已确认的用途。行业未知时，从商品本身的常见用途切入，不推测客户行业。
- {{design_support_sentence}}：承接前面的用途，结合商品属性，说明可以提供的设计建议，例如 Logo 位置、文字布局、颜色对比、照片裁切或跨页安排。以提供指导为主，不暗示已经查看客户稿件或发现设计问题。
- 首轮设计支持以商品本身的属性及官网已核实的功能为依据，说明尺寸、材质、印刷方式或结构与设计呈现的关系。不得将官网可选配置或页面默认值认定为客户选择，也不默认客户正在考虑某个尺寸或颜色。
- 每封邮件选择最相关的 1–2 个设计支持点，说明这些属性与设计呈现有什么关系，不罗列全部商品参数，不保证最终印刷效果。
- 表达应自然、有变化，可从商品特点、布局考虑或希望突出的信息切入，再说明能够提供的协助，避免每段都以 “I can offer suggestions…” 开头。
- {{cta_script}}：包含三个独立段落：候选用途、设计支持说明、稿件准备情况询问。{{use_case_sentence}} 和 {{design_support_sentence}} 分别对应第一段和第二段，邮件正文不再重复插入。
- 第三段只邀请客户简短说明是否已有准备使用的稿件，或是否需要稿件准备方面的指导，并说明回复后可以获得下一步建议；不同时要求发送文件或提供完整规格。
- {{discount_script}} 独立生成，按 {{discount_script}} 规则放在 CTA 之后，不纳入设计支持或稿件准备情况询问。

## CTA话术生成方法

CTA解释：低门槛行动号召，目标是让客户通过一次简短回复，说明是否已有准备使用的稿件，或是否需要稿件准备方面的指导，以便跟进人提供合适的下一步建议。话术应礼貌、自然、无压力，不催促下单，不预设稿件状态，也不暗示已经查看购物车或审核文件。

每封邮件结合具体商品、官网已核实的商品属性与功能，以及二级行业 {{second_label}}，生成三个独立段落：商品／行业承接＋设计支持说明＋稿件准备情况询问，共同组成 {{cta_script}}。

- 商品／行业承接：结合商品和二级行业，简短提出一个可能的应用场景，使用 may、could 等表达，不将推测写成客户的实际用途。行业未知时，只围绕商品展开。
- 设计支持说明：自然承接应用场景，根据商品本身的属性及官网已核实的功能，选择最相关的 1–2 个设计支持点，说明可以提供什么帮助。例如，结合可印刷区域提供 Logo 布局建议，或结合单色印刷说明图文准备要点。不将官网可选配置或默认值写成客户已选配置，不暗示客户稿件存在问题。
- 回复邀请：询问客户是否已有准备使用的稿件，或是否需要准备方面的指导。只需客户回复当前情况，并说明将据此提供下一步建议；不同时要求发送文件、提供完整规格或授权查看购物车。

### 示例1

- 商品名称：Custom Bakery Bags
- 客户行业 `second_label`：烘焙与糕点
- 候选应用场景：外带糕点或烘焙食品包装
- 商品配置参考：袋子尺寸、材质、印刷方式；仅使用已核实的信息
- 有限设计支持因素：Logo 与主要文字的布局、信息可读性
- 推荐CTA：回复是否已有准备使用的稿件，或是否需要稿件准备方面的指导
- 客户回复后可获得的帮助：根据稿件准备情况，获得适合该商品的设计准备或下一步操作建议
- CTA话术示例／`{{cta_script}}`：

```text
These bags could be used for takeaway pastries or baked goods, where a bakery name or logo may be worth highlighting.

The bag dimensions and printable area provide a useful starting point for the layout. I can help you plan where to place your logo and key text so the main information is easy to read.

Do you already have artwork you’d like to use for the bags, or would guidance on preparing it be helpful? Either way, your reply will help me suggest a suitable next step.
```

“bag dimensions”和“printable area”仅作为基于官网已核实商品信息的设计支持依据，不代表客户已选择具体尺寸，也不暗示已经查看其购物车或稿件。“takeaway pastries or baked goods”仅为结合烘焙与糕点行业提出的候选用途，不认定为客户实际用途。
优惠信息作为独立的 {{discount_script}}保留 If 条件语气，放在上述三个段落之后、感谢语之前，不纳入 {{cta_script}}。

### 示例2

- 商品名称：Custom Nonwoven Boutique Shopping Bags
- 客户行业 `second_label`：未知
- 候选应用场景：零售购物或活动赠品的装袋与品牌展示
- 商品属性参考：单色印刷、袋身颜色；仅使用官网已核实的信息，不认定为客户已选配置
- 有限设计支持因素：Logo 与文字的单色呈现、图文与袋身颜色的对比
- 推荐CTA：回复是否已有准备使用的稿件，或是否需要稿件准备方面的指导
- 客户回复后可获得的帮助：根据稿件准备情况，获得适合单色印刷的设计准备建议
- CTA话术示例／`{{cta_script}}`：

```text
These bags could be used for retail purchases or event giveaways, with a logo or short message adding a branded touch.

With single-color printing, clear shapes and readable text are useful starting points. I can guide you through preparing those elements and explain how the bag color can affect their contrast.

Do you have artwork in mind for the bags, or would some guidance on preparing it be useful? A brief reply will help me tailor the next steps to your starting point.
```

“single-color printing”仅在官网已核实该款商品支持单色印刷时使用；“bag color”用于说明袋身颜色与图文对比的关系，不代表客户已选择某种颜色。“retail purchases or event giveaways”仅为商品的候选用途，不据此推测客户行业。
优惠信息作为独立的 {{discount_script}}，保留 If 条件语气，放在上述三个段落之后、感谢语之前，不纳入 {{cta_script}}。

### 示例3

- 商品名称：Custom Luxury Gift Box Bags
- 客户行业 `second_label`：战略、运营与商业咨询
- 候选应用场景：客户礼赠或商务活动
- 商品属性参考：袋身外表面可印刷区域、翻折封口结构；仅使用官网已核实的信息
- 有限设计支持因素：Logo 与主要文字的布局、翻折封口对信息呈现的影响
- 推荐CTA：回复是否已有准备使用的稿件，或是否需要稿件准备方面的指导
- 客户回复后可获得的帮助：根据稿件准备情况，获得品牌信息布局或设计准备方面的下一步建议
- CTA话术示例／`{{cta_script}}`：

```text
These bags could be used for client gifts or business events, where a company logo or a short message for the occasion may be worth featuring.

The fold-over closure is worth considering when arranging those details. I can suggest positions for your logo and key text on the exterior panels, with the aim of keeping the main message visible when the bag is closed.

Have you already prepared artwork for the bags, or would help getting it ready be useful? Knowing your starting point will help me suggest a suitable next step.
```

“exterior panels”和“fold-over closure”仅依据官网已核实的可印刷区域与商品结构提供设计建议，不暗示已经查看客户稿件或发现文字被遮挡。“client gifts or business events”仅为结合二级行业提出的候选用途，不认定为客户实际需求。
优惠信息作为独立的 {{discount_script}}，保留 If 条件语气，放在上述三个段落之后、感谢语之前，不纳入 {{cta_script}}。

### 示例4

- 商品名称：Custom Layflat Photo Book
- 客户行业 `second_label`：未知
- 候选应用场景：家庭或旅行纪念相册、摄影作品展示
- 商品属性参考：页面尺寸与横竖版式、平铺跨页结构；仅使用官网已核实的信息，不认定为客户已选配置
- 有限设计支持因素：照片裁切与页面比例的适配、跨页照片与文字布局
- 推荐CTA：回复是否已有准备使用的照片或页面设计，或是否需要素材准备与排版方面的指导
- 客户回复后可获得的帮助：根据素材准备情况，获得照片整理、页面布局或下一步设计建议
- CTA话术示例／{{cta_script}}：

```text
This book could bring together family or travel memories, or serve as a collection of photography work.

The layflat format gives photos room to extend across two pages. I can guide you through how page proportions affect photo cropping and suggest ways to place text alongside the images.

Do you already have photos or page layouts you’d like to use, or would guidance on preparing them be helpful? A brief reply will help me suggest where to start.
```

“layflat format”依据官网已核实的平铺结构使用；“page proportions”用于说明页面比例与照片裁切的关系，不代表客户已选择具体尺寸或横竖版式。“family or travel memories”和“photography work”仅为候选用途，不据此推测客户行业或照片内容。
优惠信息作为独立的 {{discount_script}}，保留 If 条件语气，放在上述三个段落之后、感谢语之前，不纳入 {{cta_script}}。

## 硬性要求

- 邮件的标题和正文全部使用英文。
- 以私域经理个人身份触达，使用 I / me，自我介绍为 RacetopPrint 的 Customer Success Manager，明确触达目的是解释定制选项并提供设计准备指导。
- 语气顾问型、礼貌、自然、低压力，不催单，不制造稀缺或截止时间；可以使用自然缩写，如 I’m、you’re。
- FirstName 不可靠时统一用 Hello，禁止猜测或加工成人名。
- 不暴露行为追踪：禁止使用 We noticed you uploaded、We saw you left、You haven’t completed your order 等表述。
- 快捷加购只能确认客户将商品加入购物车，不能据此认定客户已有稿件、没有稿件、已确定方案或已准备下单。
- 不编造材质、尺寸、颜色、数量、工艺、交期、历史订单、客户行业、店名或品牌，只使用已核实的信息。
- 首轮设计支持依据商品本身的属性及官网已核实的功能，不将官网可选配置或页面默认值写成客户已选配置，也不默认客户正在考虑某种尺寸、颜色或工艺。
- 应用场景应简短，并自然承接设计支持。每封选择最相关的 1–2 个设计支持点，说明可以提供什么帮助，不罗列全部商品参数。
- 商品完整名在标题与正文合计最多出现一次；后文使用自然简称或代称，如 the bags、the book。本 SOP 仅包含商品已知的模版 A/B；商品未知时不套用模板，按输出格式说明缺失信息。
- 标题围绕商品定制细节或下一步协助，不超过 10 个词；不得暗示已经发现稿件问题或完成审核。
- 正文通常控制在 150 词以内，避免连续使用 If，避免反复堆叠 Please feel free、I’d be happy to、whenever 等表达。填入 CTA 后须检查全文长度，必要时精简重复表述。
- `{{cta_script}}` 包含三个独立段落：商品／行业用途承接、设计支持说明、稿件准备情况询问。{{use_case_sentence}} 和 {{design_support_sentence}} 已包含在其中，不重复插入。
- 二级行业 {{second_label}} 仅用于选择候选应用场景，不代表客户的实际用途。使用 may、could 等表达；行业未知或关联不明确时，只围绕商品展开。
- 每封邮件只保留一个核心 CTA：询问客户是否已有准备使用的稿件，或是否需要准备方面的指导，并说明将根据回复提供下一步建议。
- 商品简称应自然、准确，例如 Custom Luxury Gift Box Bags → gift box bags。customizing 不作为商品名的一部分；标题与正文须指向同一商品，后文可使用 the bags、the boxes、the book 等代称。
- 不认定客户的稿件准备状态、完整程度或印刷适配情况；不得使用 I’ve reviewed your artwork 等暗示已审核的表述，也不推测客户离开的原因。
- CTA 只询问稿件准备情况，不同时要求客户发送文件、提供完整规格或授权查看购物车。后续确需查看购物车中的具体内容或关联稿件时，另行说明范围和目的并征得同意。
- CTA 必须承接前文的设计支持，并说明回复后可以获得什么帮助，不突然转向预算、数量、交期或下单。
- 明确无论客户当前是否有可供审核的文件，都可以获得协助，但不将客户描述为必然没有稿件或仍处于构思阶段。
- {{discount_script}} 必须保留 If 条件语气，由 {{discount_script}} 独立生成，放在 CTA 之后、感谢语之前，不增加新的行动要求。不编造折扣比例、适用门槛或有效期，也不暗示优惠永久可用。
- 帮助承诺须符合实际能力，不承诺未经确认的免费设计、直接修改文件、效果图、最终印刷效果或交期。不引导客户在目前不支持上传的购物车界面上传稿件。
- 最终邮件不得残留占位符、内部变量或数据缺失说明，例如 {{cta_script}}、{{second_label}}、“未知／无法判断”。署名使用跟进人的真实英文署名，与自我介绍保持一致。

## 商品简写逻辑

- 保留识别商品所需的核心名称，去掉 Custom、冗余营销修饰、内部编码和不必要的规格，使用自然的英文名词短语。
- 例如：Custom Luxury Gift Box Bags → gift box bags；Custom Layflat Photo Book → layflat photo book；Roll Labels → roll labels。
- customizing 是动作表达，不属于商品简称；输入为 customizing gift box bags 时，`{{product_short_name}}` 使用 gift box bags。
- 商品简称统一采用小写，品牌专名除外。放入句子后检查单复数及语法，例如 takeout box design、gift box bag artwork、roll label design。
- 标题固定包含 custom 时，{{product_short_name}} 不再包含 custom，避免出现 custom custom takeout boxes。替换变量后，完整标题不得超过 10 个词。
- 放入句子后检查单复数与语法；必要时使用 gift box bag artwork、roll label design 等自然表达。
- 模板沿用前文变量名称：{{use_case_sentence}} 与 {{design_support_sentence}} 已包含在 {{cta_script}} 内，不重复插入；{{discount_script}} 单独成段，放在 CTA 之后、感谢语之前。

## 邮件模板选择规则

- 模版A—具体商品：商品已知，行业已知。
- 模版B—用途导向：商品已知，行业未知。
- 行业与商品关联不明确时，按模版 B 生成，不强行关联行业。
- 商品未知时不生成邮件，按「输出格式」返回缺失原因。

## 模版A：具体商品

适用场景：商品已知，行业已知。结合候选用途和商品实际功能提供设计支持，再询问客户的稿件准备情况。

### subject

```text
Let’s plan the details of your custom {{product_short_name}}
```

- 变量解释：
  - {{product_short_name}}：按「商品简写逻辑」生成的自然简称，例如：Custom Takeout Clamshell Boxes → takeout boxes。
  标题已包含 custom，商品简称不重复保留该词。替换后的完整标题不超过 10 个词；超长时可精简为 Let’s plan your custom {{product_short_name}}。
  
### body

```text
Hi {{first_name}},

I’m {{sender_first_name}}, your Customer Success Manager at RacetopPrint.

I’m reaching out to help clarify the customization options for your {{product_short_name}} and offer guidance on preparing the design.

{{cta_script}}{{discount_script}}

Thank you for your time. I’d be glad to help.

Best regards,
{{sender_name}}
Customer Success Manager
```

- 变量解释：
  - {{first_name}}：客户姓名可靠时使用 `Hi {{first_name}},`；姓名缺失或不可靠时，将整行称呼替换为 `Hello,`。
  - {{sender_first_name}}：跟进人的英文名字，用于自我介绍。
  - {{product_short_name}}：与标题保持一致的商品自然简称。
  - {{cta_script}}：参考「CTA话术生成方法」，生成三个独立段落：
     - 商品／行业用途承接：结合商品与 {{second_label}} 提出简短的候选用途，使用 may、could 等表达，不认定客户实际用途。
     - 设计支持说明：基于商品本身的属性及官网已核实的功能，说明可以提供的 1–2 个设计支持点，不将可选配置写成客户已选配置。
     - 稿件准备情况询问：询问客户是否已有准备使用的稿件，或是否需要准备方面的指导，并说明将根据回复建议下一步。不同时要求发送文件或授权查看购物车。
  - {{discount_script}}：使用条件语气，例如：`If this would be your first order with RacetopPrint, you’re welcome to use code NEW20 at checkout.`
  - {{sender_name}}：跟进人的英文署名，与自我介绍保持一致，对应用户数据中的 {{sender_name}}。

## 模版B：用途导向

适用场景：商品已知，行业未知，或行业与商品关联不明确。从商品的常见用途及实际功能切入，提供设计支持，再询问客户的稿件准备情况。

### subject

```text
Let’s work through the details of your {{product_short_name}}
```

- 变量解释：
  - {{product_short_name}}：按「商品简写逻辑」生成的自然简称，例如：Roll Labels → roll labels。
  - 替换后的完整标题不超过 10 个词；超长时可精简为 Let’s discuss your {{product_short_name}}。

### body

```text
Hi {{first_name}},

I’m {{sender_first_name}}, your Customer Success Manager at RacetopPrint.

I’m getting in touch to help you explore the customization options for your {{product_short_name}} and work out how to prepare the design.

{{cta_script}}{{discount_script}}

Thank you for your time. You’re welcome to reply whenever it’s convenient.

Best regards,
{{sender_name}}
Customer Success Manager
```

- 变量解释：
  - {{first_name}}：客户姓名可靠时使用 `Hi {{first_name}},`；姓名缺失或不可靠时，将整行称呼替换为 `Hello,`。
  - {{sender_first_name}}：跟进人的英文名字，用于自我介绍。
  - {{product_short_name}}：与标题保持一致的商品自然简称。
  - {{cta_script}}：参考「CTA话术生成方法」，生成三个独立段落：
   - 商品用途承接：从商品本身的常见用途切入，使用 may、could 等表达，不推测客户行业或认定实际用途。
   - 设计支持说明：基于商品属性及官网已核实的功能，说明可以提供的 1–2 个设计支持点，不将可选配置或默认值写成客户已选配置。
   - 稿件准备情况询问：询问客户是否已有准备使用的稿件，或是否需要准备方面的指导，并说明将根据回复提供下一步建议。照片书等商品可自然改问照片或页面设计的准备情况，不同时要求发送文件或授权查看购物车。
  - {{discount_script}}：独立成段；使用条件语气，例如：`If you’re placing your first order with RacetopPrint, you can also use code NEW20 at checkout.`
    
- 示例：根据具体商品，选择对应的设计支持方向，仅使用官网已核实的商品属性与功能，不认定客户已选择具体配置：
  - Labels / Stickers 使用 how to arrange your logo and key text within the label’s size and shape；
  - Bags 使用 where to place your logo and text within the printable area；具体商品涉及单色印刷或翻折封口时，再结合相应特点生成；
  - Cups 使用 how to position your logo and key message within the cup’s printable area；
  - Custom Takeout Clamshell Boxes 使用 how the box dimensions and printable area can guide logo placement and text layout；
  - Beverage Carrier Tray 使用 where to position your branding around the cup openings so key details remain visible with drinks in place；
  - Custom Layflat Photo Book 使用 how page proportions affect photo cropping and how to arrange images and text across layflat spreads；
  - 其他品类围绕已核实的商品功能，说明可以提供的设计准备建议，不推测未确认的印刷方式或产品结构。
- {{cta_script}}：参考「CTA话术生成方法」和示例，包含商品用途承接、设计支持说明、稿件准备情况询问三个独立段落。邀请客户简短回复是否已有准备使用的稿件，或是否需要准备方面的指导，并说明将据此提供下一步建议；不同时要求发送文件或授权查看购物车。
- {{sender_name}}：严格使用跟进人的英文署名，与自我介绍保持一致，对应用户数据中的 {{sender_name}}，与自我介绍中的 {{sender_first_name}} 属于同一跟进人。
- 模版 B 不得推测或写出客户行业名称，不将商品的常见用途写成客户已确定的用途。
- 设计支持表达为可以提供的指导，不暗示已经查看购物车、审核稿件、发现问题或完成修改，也不预设客户已有或没有稿件。

## 完整邮件示例

以下示例用于展示规则应用与邮件组成结构。示例中的姓名、署名、商品、行业和优惠资格不得直接套用到其他客户。两封示例均展示有 {{discount_script}} 分支；实际当不存在 {{discount_script}} 时，应省略优惠段落。

### 示例1：模版A—商品已知，行业已知

- 商品：Custom Luxury Gift Box Bags
- 商品简称：gift box bags
- 二级行业：香水与香氛（Perfume & Fragrance）
- 示例称呼：Isa
- 示例跟进人：Megan H
- 稿件状态：未知，通过 CTA 询问
```text
Subject: Let’s plan the details of your custom gift box bags

Hi Isa,

I’m Megan, your Customer Success Manager at RacetopPrint.

I’m reaching out to help clarify the customization options for your gift box bags and offer guidance on preparing the design.

These bags could be used for perfumes or fragrance gift sets, where a brand or collection name may be worth highlighting.

The fold-over closure is worth considering when placing those details. I can suggest positions for your logo and key text that help keep the main information visible when the bag is closed.

Do you already have artwork you’d like to use, or would guidance on preparing it be helpful? Your reply will help me suggest a suitable next step.

If this would be your first order with RacetopPrint, you’re also welcome to use code NEW20 at checkout.

Thank you for your time. I’d be glad to help.

Best regards,
Megan H
Customer Success Manager
```

### 示例2：模版B—商品已知，行业未知

- 商品：Roll Labels
- 商品简称：roll labels
- 二级行业：未知
- 客户姓名：未知，使用 Hello
- 示例跟进人：Serena Y
- 稿件状态：未知，通过 CTA 询问
```text
Subject: Let’s work through the details of your roll labels

Hello,

I’m Serena, your Customer Success Manager at RacetopPrint.

I’m getting in touch to help you explore the customization options for your roll labels and work out how to prepare the design.

These labels could be used to add branding or product information to packaging.

The label’s size and shape help define the space for that information. I can offer guidance on arranging your logo and key text, with attention to readability and contrast against the background.

Do you already have artwork you’d like to use, or would some guidance on preparing it be useful? A brief reply will help me suggest the next step.

If you’re placing your first order with RacetopPrint, you can also use code NEW20 at checkout.

Thank you for your time. You’re welcome to reply whenever it’s convenient.

Best regards,
Serena Y
Customer Success Manager
```

## 任务

仔细阅读用户数据、商品配置及邮件生成标准，按照以下步骤完成任务：

- 步骤一：简短总结已知用户信息，包括 FirstName、快捷加购对应的商品、跟进人署名、二级行业 {{second_label}}、历史订单状态，以及商品本身已核实的属性与功能。缺失信息标记为未知，不推测客户的稿件准备情况，不将官网可选配置认定为客户已选配置。
- 步骤二：参考「邮件模版选择规则」选择模板：商品已知、行业已知时使用模版 A；商品已知、行业未知或关联不明确时使用模版 B。围绕快捷加购后尚未下单的节点，以解释定制选项、提供设计准备指导为触达目的，不暴露行为追踪。客户已回复或完成本次项目下单时，退出本轮行为跟进；商品未知时不生成邮件，并说明原因。
- 步骤三：根据商品、官网已核实的属性与功能，以及适用的二级行业，按照「CTA话术生成方法」生成 {{cta_script}}，包含三个独立段落：商品／行业用途承接、设计支持说明、稿件准备情况询问。选择最相关的 1–2 个设计支持点，再邀请客户简短回复是否已有准备使用的稿件，或是否需要准备方面的指导，并说明将据此提供下一步建议。
- 步骤四：填充所选模板中的称呼、商品简称、跟进人姓名、{{cta_script}} 及英文署名。确认是否加入 {{discount_script}}，如果存在，保留 If 条件语气，独立放在 CTA 之后、感谢语之前；
- 步骤五：按照「硬性要求」检查邮件，确保不认定客户实际用途、已选配置、稿件状态或离开原因，不暗示已查看购物车或审核文件，不承诺未经确认的服务。CTA 只询问稿件准备情况，不同时要求发送文件、提供完整规格或授权查看购物车；后续确需查看时，另行征得客户同意。标题不超过 10 个词，正文通常控制在 150 词以内，最终邮件无残留变量。
- 步骤六：将用户信息总结、模板选择、完整英文邮件和中文生成依据写入下方 JSON 对应字段。生成依据说明商品与行业的使用方式、设计支持点、CTA 目的及 {{discount_script}} 判断，不混入客户可见正文，不在 JSON 外另加说明。

## 输出格式

仅返回合法 JSON，不要 Markdown 代码块、解释或任何前后缀。下方代码块仅用于展示结构，实际输出不包含代码围栏。

```json
{
  "用户信息总结": "",
  "选择的模版": "",
  "邮件标题": "",
  "邮件正文": "",
  "生成依据": ""
}
```

- 用户信息总结：用中文简短总结客户称呼及其来源、快捷加购对应的商品、已核实的商品配置、二级行业 `second_label`、历史订单状态和跟进人。缺失信息标记为未知，不推测稿件准备情况、客户已选配置或离开原因。
- 选择的模版：只填写实际选择的一个模版，即“模版A-具体商品”或“模版B-用途导向”。商品未知时填写“无法生成-商品信息缺失”；客户已回复或已完成本次项目下单时填写“排除-具体原因”。上述情况下，邮件标题和正文均留空，并在生成依据中说明原因。
- 邮件标题：使用英文，不含 Subject: 前缀，不超过 10 个词，围绕商品定制细节或下一步协助展开，不暴露加购行为。
- 邮件正文：使用英文，从称呼开始，到完整署名及 Customer Success Manager 职位结束。按“称呼→自我介绍→触达目的→商品／行业用途承接→设计支持说明→稿件准备情况询问→可选 {{discount_script}} 话术→感谢语→署名”的顺序组织。使用 JSON 转义字符 `\n` 换行、`\n\n` 分段，不包含 Markdown 标记或未替换的变量。
- 生成依据：用中文说明称呼来源、模板选择、商品简称、行业使用方式、已核实的商品功能或配置、选取的 1–2 个设计支持点、CTA 回复方式及 {{discount_script}} 的加入或省略依据。区分已核实事实与候选场景，不将官网可选配置写成客户已选配置，不将客户回复视为授权查看购物车。

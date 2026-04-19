# -*- coding: utf-8 -*-
"""Merge new pinyin-word pairs; skip any (pinyin,word) already present in assets."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app" / "src" / "main" / "assets"
OUT_NAME = "pinyin_words_extended_batch_a.txt"

SOURCE_FILES = [
    "pinyin_words.txt",
    "car_brands.txt",
    "pinyin_words_poetry.txt",
    "pinyin_words_food.txt",
    "pinyin_words_countries.txt",
    "pinyin_words_modern.txt",
    "pinyin_append_temp.txt",
    "wordlist_idioms.txt",
    "wordlist_astronomy.txt",
    "wordlist_daily.txt",
]


def parse_file(path: Path) -> set[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    if not path.exists():
        return seen
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        sp = line.find(" ")
        if sp <= 0:
            continue
        py = line[:sp].lower().replace(" ", "")
        w = line[sp + 1 :].strip()
        if py and w:
            seen.add((py, w))
    return seen


def load_existing() -> set[tuple[str, str]]:
    acc: set[tuple[str, str]] = set()
    for name in SOURCE_FILES:
        acc |= parse_file(ASSETS / name)
    return acc


def split_pairs(block: str) -> list[tuple[str, str]]:
    """每行「拼音 词」；忽略 # 注释。"""
    out: list[tuple[str, str]] = []
    for raw in block.strip().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        sp = line.find(" ")
        if sp <= 0:
            continue
        py = line[:sp].lower().strip()
        word = line[sp + 1 :].strip()
        if py and word:
            out.append((py, word))
    return out


def build_lexicon_extra() -> list[tuple[str, str]]:
    """节气、节日食品、前 40 号元素中文名、互联网与政务常用词（逐行校验）。"""
    text = """
lichun 立春
yushui 雨水
jingzhe 惊蛰
chunfen 春分
qingming 清明
guyu 谷雨
lixia 立夏
xiaoman 小满
mangzhong 芒种
xiazhi 夏至
xiaoshu 小暑
dashu 大暑
liqiu 立秋
chushu 处暑
bailu 白露
qiufen 秋分
hanlu 寒露
shuangjiang 霜降
lidong 立冬
xiaoxue 小雪
daxue 大雪
dongzhi 冬至
xiaohan 小寒
dahan 大寒
yuanxiaojie 元宵节
qingmingjie 清明节
duanwujie 端午节
zhongqiujie 中秋节
chongyangjie 重阳节
labajie 腊八节
hanlujie 寒衣节
qing 氢
hai 氦
li 锂
pi 铍
peng 硼
tan 碳
dan 氮
yang 氧
fu 氟
nai 氖
na 钠
mei 镁
lv 铝
gui 硅
lin 磷
liu 硫
lv 氯
ya 氩
jia 钾
gai 钙
kang 钪
tai 钛
fan 钒
ge 铬
meng 锰
tie 铁
gu 钴
nie 镍
tong 铜
xin 锌
jia 镓
zhe 锗
shen 砷
xi 硒
xiu 溴
dian 碘
xian 氙
paichusuo 派出所
minjing 民警
xiaofangyuan 消防员
jiuhuche 救护车
jiuyuan 救援
shebaoju 社保局
jiaoyuju 教育局
weishengju 卫生局
zhujianju 住建局
shuiwuju 税务局
shouxuji 手机壳
pingbandiannao 平板电脑
xianshiqi 显示器
neicun 内存
xianshika 显卡
wangka 网卡
shexiangtou 摄像头
maikefeng 麦克风
chongdianqi 充电器
shujuxian 数据线
luyouqi 路由器
yasuobao 压缩包
wendangjia 文件夹
caozuoxitong 操作系统
shujufenxi 数据分析
dashuju 大数据
renkongzhineng 人工智能
shenduxuexi 深度学习
jiqixuexi 机器学习
yunfuwu 云服务
gongyouyun 公有云
siyouyun 私有云
qukuailian 区块链
xunixianshi 虚拟现实
zengqiangxianshi 增强现实
zhibojian 直播间
daihuo 带货
baokuan 爆款
banbenhao 版本号
fuwuqi 服务器
duankou 端口
renzheng 认证
shouquan 授权
yunweigongchengshi 运维工程师
chanpinjingli 产品经理
kehujingli 客户经理
xiangmujingli 项目经理
yuangong 员工
laodonghetong 劳动合同
shebao 社保
gongjijin 公积金
kaoqin 考勤
qingjia 请假
jiaban 加班
biaoge 表格
huiyishi 会议室
bangongshi 办公室
"""
    return split_pairs(text)


def build_lexicon_extra_round2() -> list[tuple[str, str]]:
    """第二批：医疗、法律、校园、农林牧渔、家务与情绪表达（相对成语库重叠较少）。"""
    text = """
neike 内科
waike 外科
erke 儿科
fuke 妇科
chanke 产科
yanke 眼科
erbihouke 耳鼻喉科
pifuke 皮肤科
guke 骨科
shenjingke 神经科
xinneike 心内科
xinwaike 心外科
xiaohuaneike 消化内科
huxineike 呼吸内科
zhongliuke 肿瘤科
mazuike 麻醉科
fangshexianke 放射科
chaoshengke 超声科
binglike 病理科
jianyanke 检验科
yaofang 药房
zhuyuanbu 住院部
menzhenbu 门诊部
jizhenke 急诊科
bingfang 病房
bingchuang 病床
huoshi 护士站
tuoye 退热
zhitong 止痛
xiaoyan 消炎
zhike 止咳
huatan 化痰
jiangya 降压
jiangtang 降糖
shuuye 输液
zhusheye 注射液
koufuyao 口服药
waiyong 外用
guominshi 过敏史
bingli 病历
binglihao 病历号
jiuzhenka 就诊卡
guahaofei 挂号费
menzhenfei 门诊费
zhuyuanfei 住院费
shoushufei 手术费
jianchafei 检查费
huayan 化验
paichao 拍片
CTjiancha CT检查
hecigongzhen 核磁共振
chaosheng 超声
xindiantu 心电图
bingligaoshi 病理报告
zhuyuan 住院
chuyuan 出院
zhuanke 转科
zhuanzhen 转诊
huiyi 会诊
shoushu 手术
quanma 全麻
banma 半麻
fengzhen 缝合
jiancha 检查
fucha 复查
suifang 随访
baojianpin 保健品
weishengsu 维生素
gaoxuezhi 高血脂
gaoniaosuan 高尿酸
tongfeng 痛风
jiazhuangxian 甲状腺
jiazhuangxiangongneng 甲状腺功能
tangniaobing 糖尿病
guanxinbing 冠心病
naoxueshuan 脑血栓
naochuxue 脑出血
zhongfeng 中风
chanhou 产后
yunjian 孕检
chanjian 产检
minfadian 民法典
xingfa 刑法
xingsusongfa 刑事诉讼法
minsusongfa 民事诉讼法
xingzhengsusongfa 行政诉讼法
hetongfa 合同法
laodongfa 劳动法
gongsifa 公司法
shuifa 税法
zhishichanquan 知识产权
zhuanli 专利
shangbiao 商标
banquan 版权
mimi 秘密
shangyejimi 商业秘密
baomi 保密
xieyi 协议
heyue 合约
weiyue 违约
peichang 赔偿
buchang 补偿
hejie 和解
tiaojie 调解
zhongcai 仲裁
susong 诉讼
qisu 起诉
gaozhuang 告状
beigao 被告
yuangao 原告
dalishi 大律师
faquan 法权
renquan 人权
caichan 财产
yichan 遗产
jicheng 继承
yizhu 遗嘱
lihun 离婚
jiehun 结婚
fuyang 抚养
qiangzhizhixing 强制执行
panjue 判决
caiding 裁定
weifaxingwei 违法行为
weifajingying 违法经营
xingzhengchufa 行政处罚
juliu 拘留
xingjing 刑警
jiaojing 交警
wangjing 网警
zhian 治安
paichusuo 所长
jingcha 警察
jianyu 监狱
jiuzheng 纠正
jiazhanghui 家长会
banzhuren 班主任
kebiao 课表
zuoyehen 作业本
shiyanbao 实验报告
kaoshijuan 考试卷
manfen 满分
jige 及格
bujige 不及格
liujia 留级
tiaoji 跳级
baoyan 保研
kaobo 考博
zhuanke 专科
benkesheng 本科生
shuoshisheng 硕士生
boshi 博士生
boshi 博士
bochihou 博士后
shuxueke 数学课
yingyuke 英语课
yuwenke 语文课
wulike 物理课
huaxueke 化学课
shengwuke 生物课
lishike 历史课
dilike 地理课
tiyuke 体育课
meishuke 美术课
yinyueke 音乐课
xinxike 信息课
xuanxiuke 选修课
bixiuke 必修课
tongyongke 通识课
qimokaoshi 期末考试
qizhongkaoshi 期中考试
suitangceyan 随堂测验
zuoyejiancha 作业检查
hanjia 寒假
shujia 暑假
kejian 课间
zaodu 早读
wanzixi 晚自习
shitang 食堂
sushe 宿舍
xiaomen 校门
jiaoshi 教室
jiangtai 讲台
heiban 黑板
baiban 白板
touyingyi 投影仪
jiaocai 教材
jiaofei 教辅
ketang 课堂
xiaoke 小课
daoke 大课
zhongzi 种子
huafei 化肥
nongyao 农药
chucao 除草
guangai 灌溉
shouge 收割
bozhong 播种
chulan 出栏
siliao 饲料
muji 母鸡
gongji 公鸡
zhuzai 猪仔
niudu 牛犊
yanggao 羊羔
yumi 玉米
daogu 稻谷
xiaomai 小麦
dadou 大豆
huasheng 花生
mianhua 棉花
shucai 蔬菜
shuiguo 水果
chaye 茶叶
sangye 桑叶
fengmi 蜂蜜
yangfeng 养蜂
yutang 鱼塘
yangzhi 养殖
diaoyu 钓鱼
buke 补课
buchong 补充
tuoguan 托管
tuoxiao 滞销
fengshou 丰收
jiaqin 家禽
jiaxu 家畜
tuona 拖沓
tuola 拖拉
tuoxie 拖鞋
tuoxie 妥协
tuoxiao 脱销
saodi 扫地
tuodi 拖地
cawan 擦碗
xiyifu 洗衣服
shaiyifu 晒衣服
diebeizi 叠被子
zhunbeifan 准备饭
zuofan 做饭
shaofan 烧饭
chufang 厨房
youyanji 油烟机
weibolu 微波炉
dianfanguo 电饭锅
yaoshui 药水
yaopin 药品
yaodian 药店
zhenjiu 针灸
tuina 推拿
anmo 按摩
guasha 刮痧
baohuo 拔火罐
duanlian 锻炼
jianfei 减肥
zengfei 增肥
kun 困
lei 累
fan 烦
men 闷
huang 慌
pa 怕
jinzhang 紧张
fangsong 放松
gaoxing 高兴
nanguo 难过
shangxin 伤心
kaixin 开心
manyi 满意
bumanyi 不满意
youyu 犹豫
jueding 决定
fangqi 放弃
jianchi 坚持
nuli 努力
toulan 偷懒
tuoyan 拖延
zhunshi 准时
chidao 迟到
zaotui 早退
kuanggong 旷工
jinji 晋级
jiangji 降级
tisheng 提升
xiajiang 下降
"""
    return split_pairs(text)


def build_lexicon_extra_round3() -> list[tuple[str, str]]:
    """第三批：体育运动、菜系调料与烹饪、法律文书、影视音乐、房产开发术语。"""
    text = """
tianjing 田径
tiaoshui 跳水
ticao 体操
juzhong 举重
sheji 射击
shejian 射箭
jijian 击剑
mashu 马术
gaoerfu 高尔夫
saiche 赛车
malasong 马拉松
sinuoke 斯诺克
paiqiu 排球
wangqiu 网球
pingpangqiu 乒乓球
lanqiu 篮球
zuqiu 足球
yumaoqiu 羽毛球
bangqiu 棒球
qugun 曲棍球
bingqiu 冰球
huaxue 滑雪
huaban 滑板
lunhua 轮滑
jiqirensai 机器人赛
aolinpike 奥林匹克
yazhoubei 亚洲杯
shijiebei 世界杯
jiaolian 教练
duiyuan 队员
duizhang 队长
tibu 替补
canjia 参赛
taijiquan 太极拳
baguazhang 八卦掌
xingyiquan 形意拳
yumao 羽毛
wangpai 网拍
qiupai 球拍
chuancai 川菜
yuecai 粤菜
lucai 鲁菜
huaiyangcai 淮扬菜
xiangcai 湘菜
mincai 闽菜
zhecai 浙菜
huicai 徽菜
dongbei 东北菜
xican 西餐
rihanliao 日韩料理
huoguo 火锅
shaokao 烧烤
chuanchuan 串串
malatang 麻辣烫
xiaolongbao 小笼包
jiaozi 饺子
baozi 包子
mantou 馒头
youtiao 油条
doujiang 豆浆
zhou 粥
mifan 米饭
chaomian 炒面
chaofan 炒饭
tanmian 汤面
lamian 拉面
guotie 锅贴
choudoufu 臭豆腐
tangcu 糖醋
hongshao 红烧
qingzheng 清蒸
ganbian 干煸
liangban 凉拌
chao 炒
zha 炸
jian 煎
men 焖
dun 炖
zhu 煮
chao 焯
chaoshui 焯水
guoyou 过油
gouqian 勾芡
fanqiejiang 番茄酱
salajiang 沙拉酱
huangdoujiang 黄豆酱
tianmianjiang 甜面酱
doubanjiang 豆瓣酱
haoyou 蚝油
shengchou 生抽
laochou 老抽
liaojiu 料酒
cu 醋
tang 糖
yan 盐
weijing 味精
jijing 鸡精
huajiao 花椒
bajiao 八角
gui 桂皮
rougui 肉桂
dingxiang 丁香
xiaohuixiang 小茴香
ziran 孜然
cong 葱
jiang 姜
suan 蒜
xiangcai 香菜
xiaomila 小米辣
lajiao 辣椒
heye 荷叶
huangyou 黄油
niunai 牛奶
suannai 酸奶
qisuzhuang 起诉状
dabianzhuang 答辩状
shangsuzhuang 上诉状
shenqingshu 申请书
shouquanweituo 授权委托
weituoshu 委托书
shouquanshu 授权书
lvshihan 律师函
gongzhengshu 公证书
hedingshu 核定书
jianzhenggao 见证书
xieyishu 协议书
hejieshu 和解书
minshianjian 民事案件
xingshianjian 刑事案件
xingzhenganjian 行政案件
minjianjiedai 民间借贷
laodongzhengyi 劳动争议
jiaotongshigu 交通事故
chanquanjiufen 产权纠纷
zhishichanquan 知识产权
panjueshu 判决书
caidingshu 裁定书
tiaojieshu 调解书
budongchan 不动产
maopi 毛坯
jingzhuang 精装
jiazhuang 家装
gongtan 公摊
rongjilv 容积率
taoneimianji 套内面积
jianzhumianji 建筑面积
ershoufang 二手房
xinfang 新房
shoufu 首付
daikuan 贷款
huankuan 还款
lixi 利息
zulin 租赁
zhuangxiu 装修
wuye 物业
yezhu 业主
yezhuweiyuanhui 业主委员会
daoyan 导演
bianju 编剧
zhipian 制片
shexiang 摄像
houqi 后期
shaji 杀青
luyan 路演
shouying 首映
piaofang 票房
duanju 短剧
wangju 网剧
weidianying 微电影
peiyue 配乐
zuoci 作词
zuoyue 作曲
bianqu 编曲
luyin 录音
pengpai 棚拍
yanchanghui 演唱会
yinyuejie 音乐节
yinyueju 音乐剧
xiqu 戏曲
jingju 京剧
yueju 越剧
huangmeixi 黄梅戏
erhu 二胡
pipa 琵琶
guzheng 古筝
gangqin 钢琴
xiaotiqin 小提琴
qianhouduan 前后端
qianduan 前端
houduan 后端
quanzhan 全栈
jiekou 接口
huidiao 回调
bingfa 并发
yibu 异步
tongbu 同步
huancun 缓存
jiqun 集群
fuwu 服务
weifuwu 微服务
rongqi 容器
bianyi 编译
jiazai 加载
bushu 部署
huixian 回滚
rizhi 日志
jiankong 监控
gaojing 告警
"""
    return split_pairs(text)


def build_lexicon_extra_round4() -> list[tuple[str, str]]:
    """第四批：气象地质、航天、金融、心理通俗词、电竞、摄影摄像、面料服装。"""
    text = """
wumai 雾霾
meiyu 梅雨
hanchao 寒潮
qiangduiliu 强对流
longjuanfeng 龙卷风
baoyu 暴雨
baoxue 暴雪
dafeng 大风
gaowen 高温
dihan 低温
chaoshi 潮湿
ganhan 干旱
nidai 逆温
zhenyu 阵雨
leiyu 雷雨
bingbao 冰雹
shachen 沙尘
yangchen 扬尘
dimao 地貌
yanjiang 岩浆
bandao 半岛
haiwan 海湾
shamo 沙漠
caodi 草地
shidi 湿地
hongshu 红树
zhaozexi 沼泽地
weixing 卫星
hangtian 航天
hangkong 航空
feichuan 飞船
yunzaihuojian 运载火箭
huojian 火箭
fazai 发射
kongjianzhan 空间站
hangtianyuan 航天员
taikong 太空
guaidao 轨道
tuokun 脱困
duijie 对接
fanhui 返回
ceshi 测控
yaogan 遥感
daohang 导航
beidou 北斗
gps GPS
gupiao 股票
jijin 基金
zhaiquan 债券
qiquan 期权
qihuo 期货
baozhengjin 保证金
baocang 爆仓
rongduan 熔断
dieting 跌停
zhangting 涨停
kaipan 开盘
shoupan 收盘
yangxian 阳线
yinxian 阴线
fenhong 分红
peigu 配股
zengfa 增发
xunihuobi 虚拟货币
zhifubao 支付宝
yinlian 银联
xinyongka 信用卡
jiebei 借呗
huabei 花呗
fenqi 分期
huankuan 还款
lixi 利息
nixi 逆势
yiyu 抑郁
jiaolv 焦虑
qiangpozheng 强迫症
shekong 社恐
neijuan 内卷
tangping 躺平
emo emo
xintai 心态
xinli 心理
zixun 咨询
shudao 疏导
guaji 挂机
kaigua 开挂
zudui 组队
kaihei 开黑
fuben 副本
paiwei 排位
duanwei 段位
youxi 游戏
shouyou 手游
duanwang 断网
yanchi 延迟
diuzhen 丢帧
guangquan 光圈
kuaimen 快门
ganguangdu 感光度
baoguang 曝光
duijiao 对焦
xuhua 虚化
jingshen 景深
niguang 逆光
shunguang 顺光
buchang 补偿
baipingheng 白平衡
sanjiaojia 三脚架
lvjing 滤镜
houqi 后期
jianji 剪辑
texiao 特效
chunmian 纯棉
mianma 棉麻
dilun 涤纶
yangrong 羊绒
yangmao 羊毛
zhensi 真丝
mianliao 面料
xiushen 修身
kuansong 宽松
heshen 合身
shouchi 尺码
xiukou 袖口
lingkou 领口
youshang 右上
zuoshang 左上
youxia 右下
zuoxia 左下
"""
    return split_pairs(text)


def build_lexicon_extra_round5() -> list[tuple[str, str]]:
    """第五批：工程机械与施工、航海渔业、文博策展、民俗节庆、五官口腔、花木虫鱼、快递。"""
    text = """
qizhongji 起重机
taji 塔吊
waji 挖机
chanche 铲车
jiaobanji 搅拌机
puluji 铺路机
yaluji 压路机
dianhan 电焊
qiege 切割
hanjie 焊接
zhuangpei 装配
maogu 锚固
zhijia 支架
moju 模具
zhoucheng 轴承
chilun 齿轮
chuandong 传动
jianxiu 检修
weixiu 维修
baoyang 保养
duangou 盾构
guandao 管道
fenguan 分管
fangshuiceng 防水层
baowen 保温
dinuan 地暖
qiqiang 砌墙
guanjiang 灌浆
zhuangxiu 装修
jungong 竣工
kaigong 开工
fangxian 放线
celiang 测量
haiyun 海运
gangkou 港口
matou 码头
bowei 泊位
jiaban 甲板
chuanshi 船体
yuanyang 远洋
buhuo 捕捞
yangzhi 养殖
yuye 渔业
shuichan 水产
haixiao 海啸
chaoxi 潮汐
hangbiao 航标
dengta 灯塔
langhua 浪花
taoqi 陶器
qingtongqi 青铜器
ciqi 瓷器
muzhiming 墓志铭
bowuguan 博物馆
meishuguan 美术馆
tushuguan 图书馆
wenwu 文物
cezhan 策展
zhanlan 展览
jiangjieyuan 讲解员
canguanzhe 参观者
menpiao 门票
yuyue 预约
tuanti 团体
daolan 导览
yeshu 压岁钱
nianyefan 年夜饭
baonian 拜年
chunlian 春联
fuchun 福字
denglong 灯笼
yanhua 烟花
bianpao 鞭炮
longzhou 龙舟
dengmi 灯谜
tangyuan 汤圆
yuanxiao 元宵
zaotang 澡堂
xichen 洗牙
baya 拔牙
zhuya 蛀牙
zhongya 种牙
jiaoya 矫牙
jieya 洁牙
yanke 眼科
jiemoyan 结膜炎
jinshi 近视
yuanshi 远视
sanguang 散光
seming 色盲
yinxingyanjing 隐形眼镜
zhongeryan 中耳炎
waieryan 外耳炎
bidouyan 鼻窦炎
houlong 喉咙
sangzi 嗓子
yueji 月季
luoluo 绿萝
junzilan 君子兰
diaolan 吊兰
xianrenzhang 仙人掌
duorouzhiwu 多肉植物
zhizi 栀子
guihua 桂花
molihua 茉莉花
hehua 荷花
liushu 柳树
songshu 松树
meihua 梅花
xique 喜鹊
maque 麻雀
zhiliao 知了
xishuai 蟋蟀
yinghuochong 萤火虫
hudie 蝴蝶
mifeng 蜜蜂
mayi 蚂蚁
zhizhu 蜘蛛
lanshou 揽收
jijian 寄件
tuotou 妥投
paisong 派送
qianshou 签收
zhongzhuanzhan 中转站
fenjian 分拣
lanhuo 揽货
"""
    return split_pairs(text)


def build_lexicon_extra_round6() -> list[tuple[str, str]]:
    """第六批：传统工艺、茶饮、论文与新闻、户外运动、母婴养老、能源采矿、数据结构用语。"""
    text = """
cixiu 刺绣
jingtailan 景泰蓝
jianzhi 剪纸
zhubian 竹编
mudiao 木雕
zhuanke 篆刻
taoyi 陶艺
qiqi 漆器
tangsancai 唐三彩
piyingxi 皮影戏
lianpu 脸谱
tieguanyin 铁观音
longjingcha 龙井茶
biluochun 碧螺春
puercha 普洱茶
wulongcha 乌龙茶
baihaoyinzhen 白毫银针
huacha 花茶
juhuacha 菊花茶
hongcha 红茶
heicha 黑茶
zhaiyao 摘要
guanjianci 关键词
cankaowenxian 参考文献
yinyan 引言
jielun 结论
zhixie 致谢
futu 附图
tubiao 图表
xumu 序言
shengou 审稿
jiaodui 校对
paiban 排版
faxingliang 发行量
zhuanfang 专访
xinwengao 新闻稿
shelun 社论
zhangpeng 帐篷
fangchaodian 防潮垫
dengshanzhang 登山杖
chongfengyi 冲锋衣
baowenbei 保温杯
zhinanzhen 指南针
shuidai 睡袋
tongxingzheng 通行证
ziniaoku 纸尿裤
naiping 奶瓶
naifen 奶粉
fushi 辅食
weilan 围栏
anquanzuoyi 安全座椅
taixin 胎心
yunfu 孕妇
zuoyue 月嫂
yuer 育儿
peihu 陪护
jiatingyisheng 家庭医生
jinglaoyuan 敬老院
yanglaoyuan 养老院
liaoyangyuan 疗养院
lunyi 轮椅
guaizhang 拐杖
hushenfu 护身符
meikuang 煤矿
kuangjing 矿井
kuangnan 矿难
shatang 塌方
anjian 安监
huodian 火电
shuidian 水电
fengdian 风电
guangfu 光伏
guangfudian 光伏电站
shuibeng 水泵
bianyaqi 变压器
peidian 配电
shudianxian 输电线
digui 递归
bianli 遍历
hashi 哈希
liebiao 链表
duilie 队列
zhan 栈
erchashu 二叉树
hongheishu 红黑树
pinghengshu 平衡树
tulun 图论
dongtaiguihua 动态规划
tanxin 贪心
paixu 排序
"""
    return split_pairs(text)


def build_lexicon_extra_round7() -> list[tuple[str, str]]:
    """第七批：乐器与演出、宗教场所与民俗、气象预警、编程概念、厨电海鲜零食、公文用语。"""
    text = """
sakesi 萨克斯
hechang 合唱
duzou 独奏
xiezou 协奏曲
jiaoxiangqu 交响曲
zhihui 指挥
pailian 排练
hezou 合奏
yinyueting 音乐厅
juyuan 剧院
wutai 舞台
mubu 幕布
guangshu 光束
yinxiang 音响
huatong 话筒
simiao 寺庙
fotang 佛堂
jiaotang 教堂
qingzhensi 清真寺
daoguan 道观
miaohui 庙会
xianghuo 香火
xuyuan 许愿
qifu 祈福
taifengyujing 台风预警
baoyuyujing 暴雨预警
hanchaoyujing 寒潮预警
dawuyujing 大雾预警
gaowenyujing 高温预警
dafengyujing 大风预警
kongqiwuran 空气污染
zhishu 指数
zifuchuan 字符串
zhengshu 整数
fudianshu 浮点数
buerlei 布尔型
yichang 异常
xiancheng 线程
jincheng 进程
jinchengsuo 进程锁
sisuo 死锁
xinghao 信号量
huchi 互斥
youyanji 油烟机
xiwanji 洗碗机
xiaodugui 消毒柜
pobiji 破壁机
kongqizhaguo 空气炸锅
dianshibao 电饭煲
yunwu 云雾
sanwenyu 三文鱼
daiyu 带鱼
huanghuayu 黄花鱼
shanbei 扇贝
haosheng 生蚝
duixia 对虾
longxia 龙虾
yuxia 鱼虾
xiapi 虾皮
shupian 薯片
guodong 果冻
tanghulu 糖葫芦
binggun 冰棍
naicha 奶茶
naichafen 奶茶粉
qipaoshui 气泡水
suannaiyinliao 酸奶饮料
hongniu 红牛
xuni 虚拟
huiyijiyao 会议纪要
qingjiatiao 请假条
tongzhigonggao 通知公告
hongtouwenjian 红头文件
shenpidan 审批单
liuzhuan 流转
guizhang 规章
zhidu 制度
kaohe 考核
pingfen 评分
jiangli 奖励
chengfa 惩罚
"""
    return split_pairs(text)


def build_lexicon_extra_round8() -> list[tuple[str, str]]:
    """第八批：天文地理、化工材料、出版印刷、农牧检疫、珠宝玉石、健身、无障碍设施。"""
    text = """
chidao 赤道
ziwuxian 子午线
jingxian 经线
weixian 纬线
jingweidu 经纬度
haiba 海拔
penqi 盆地
qiuling 丘陵
dongtu 冻土
huoshan 火山
yanjiang 岩浆
yanrong 岩溶
kasite 喀斯特
hongxi 虹吸
xingxi 星系
yinhexi 银河系
hengxing 恒星
xingxing 行星
liuxing 流星
yunshi 陨石
guangnian 光年
shexian 射线
chaoxi 潮汐
yinli 引力
juyixi 聚乙烯
jubingxi 聚丙烯
jubingxisuliao 聚丙烯塑料
buxiugang 不锈钢
lvhejin 铝合金
tonghejin 铜合金
ganghuaboli 钢化玻璃
youqi 油漆
tuliao 涂料
fangshuijiang 防水胶
shuzhi 树脂
xiangjiao 橡胶
kaiben 开本
jingzhuangben 精装本
pingzhuangben 平装本
banquanye 版权页
kanwubiao 勘误表
mulu 目录
duzhe 读者
bianji 编辑
meishubianji 美术编辑
yanxi 演习
jianyue 检阅
fangzhen 方阵
micaifu 迷彩服
junxun 军训
tili 体力
chulanlv 出栏率
fangyi 防疫
jianyi 检疫
geli 隔离
feizhouzhuwen 非洲猪瘟
koutiyiyimiao 口蹄疫疫苗
shouyi 兽医
muyangquan 牧羊犬
feicui 翡翠
hetianyu 和田玉
manao 玛瑙
zhenzhu 珍珠
mobao 墨宝
bojin 铂金
zuanshi 钻石
yinshi 银饰
jinshi 金饰
yangwoqizuo 仰卧起坐
fuwocheng 俯卧撑
shendun 深蹲
lashen 拉伸
reshen 热身
manpao 慢跑
kuaizou 快走
yujia 瑜伽
taiji 太极
qigong 气功
mangdao 盲道
lunyipodao 轮椅坡道
wuzhangai 无障碍
yuyintishi 语音提示
mangwen 盲文
shouyu 手语
"""
    return split_pairs(text)


def build_lexicon_extra_round9() -> list[tuple[str, str]]:
    """第九批：电力配电、污水垃圾分类、客运枢纽、刑事司法用语、家务清洁、病虫害、书画、计量。"""
    text = """
biandianzhan 变电站
peidiangui 配电柜
kaiguanxiang 开关箱
loudianbaohu 漏电保护
duanlu 短路
guozai 过载
jiebang 接地
jiezhuang 接地桩
diyadian 低压电
gaoyadian 高压电
paiwukou 排污口
wushuichulichang 污水处理厂
zhongshuichuli 中水处理
lajifenlei 垃圾分类
kehuishouwu 可回收物
youhailaji 有害垃圾
chuyulaji 厨余垃圾
canchulaji 餐厨垃圾
yangchen 扬尘
jiangzao 降噪
houcheshi 候车室
jianpiaokou 检票口
anjianmen 安检门
dengjipai 登机牌
xinglizhuanpan 行李转盘
hangbanyanwu 航班延误
tuoche 拖车
chaozai 超载
kaiche 开车
tingche 停车
qushenbao 取保候审
huanxing 缓刑
jiaoshi 假释
zhengju 证据
baozhengjin 保证金
falvyuanzhu 法律援助
lvshi 律师
tuoba 拖把
saozhou 扫帚
boji 簸箕
xijiejing 洗洁精
majin 抹布
weishengzhi 卫生纸
xishouye 洗手液
chushiji 除湿机
kongqijinghuaqi 空气净化器
yachong 蚜虫
hongzhizhu 红蜘蛛
baifenbing 白粉病
genfubing 根腐病
xiubing 锈病
yebanbing 叶斑病
kaishu 楷书
xingshu 行书
caoshu 草书
lishu 隶书
zhuanshu 篆书
shuimohua 水墨画
youhua 油画
youhuabang 油画棒
sumiao 素描
suxie 速写
xiesheng 写生
gongqing 公顷
mu 亩
haosheng 毫升
qianwashi 千瓦时
duliangheng 度量衡
biaozhun 标准品
yangpin 样品
shiyanpin 试验品
"""
    return split_pairs(text)


def build_lexicon_extra_round10() -> list[tuple[str, str]]:
    """第十批：海洋生物、地貌水系、咖啡饮品、职场与人事、前端术语、救灾公益、康复辅具。"""
    text = """
haibao 海豹
haitun 海豚
jingyu 鲸鱼
shayu 鲨鱼
shuimu 水母
haima 海马
zhangyu 章鱼
haigui 海龟
shanhu 珊瑚
shanhujiao 珊瑚礁
sandazhou 三角洲
qundao 群岛
haixia 海峡
xiagu 峡谷
pingyuan 平原
caodi 草甸
hupo 湖泊
dujiangyan 都江堰
sanxia 三峡
hongshui 洪水
nishiliu 泥石流
shantihuapo 山体滑坡
meishi 美式
natie 拿铁
kabuqinuo 卡布奇诺
moka 摩卡
nongsuo 浓缩
yanmainai 燕麦奶
doujiangfen 豆浆粉
jianli 简历
mianshi 面试
lietou 猎头
shiyongqi 试用期
zhuanzheng 转正
shuzhi 述职
fanpan 复盘
duiqi 对齐
luodi 落地
mubiao 目标
guankong 管控
okr OKR
kpi KPI
renshi 人事
xingzheng 行政
chucha 出差
baoxiao 报销
huikuan 汇款
zhuanzhang 转账
jieliu 节流
fangdou 防抖
lanjie 拦截
zhongjian 中间件
xingneng 性能
youhua 优化
shoulun 首轮
beifen 备份
huifu 恢复
zhenzai 赈灾
juanzeng 募捐
binansuo 避难所
jiuyuandui 救援队
hongshizihui 红十字会
zhiyuanzhe 志愿者
yiwugong 义工
zhutingqi 助听器
mangzhang 盲杖
fushou 扶手
"""
    return split_pairs(text)


def build_lexicon_extra_round11() -> list[tuple[str, str]]:
    """第十一批：戏曲行当、棋牌益智、木工五金、印染纺织、交通票务、宠物兽医、知识产权程序。"""
    text = """
shengdanjingmochou 生旦净末丑
wusheng 武生
qingyi 青衣
hualian 花脸
xiaosheng 小生
laosheng 老生
huadan 花旦
choujue 丑角
jingjue 净角
xiangqi 象棋
weiqi 围棋
tiaoqi 跳棋
wuziqi 五子棋
guoxiangqi 国际象棋
doudizhu 斗地主
guandan 掼蛋
majiang 麻将
tuolaji 拖拉机
paodekuai 跑得快
aihangxing 矮行星
huixing 彗星
liuxingyu 流星雨
xiaoxingxing 小行星
xingji 星际
changhe 长河
sunmao 榫卯
paozi 刨子
juzi 锯子
heye 合页
jiaolian 铰链
mensuo 门锁
menshuan 门闩
lasi 拉丝
fangzhi 纺织
yinran 印染
piaobai 漂白
tuise 褪色
ranliao 染料
buliao 布料
fangsha 纺纱
gaiqian 改签
tuipiao 退票
houbu 候补
tingyun 停运
yanwu 延误
chaoyuan 超员
manzai 满载
kongwei 空位
quchong 驱虫
quchongyao 驱虫药
yimiaoben 疫苗本
jiezhongjilu 接种记录
jueyu 绝育
jiezha 结扎
goulang 狗粮
maoliang 猫粮
guadang 挂单
zhushi 主食
xiaolingshi 小零食
longmao 龙猫
cangshu 仓鼠
yiwubohui 予以驳回
fushen 复审
wuxiaoxuangao 无效宣告
zantong 赞同
fanyi 翻译
quanliyaoqiu 权利要求
"""
    return split_pairs(text)


def build_lexicon_extra_round12() -> list[tuple[str, str]]:
    """第十二批：戏曲曲艺、民乐补充、园艺家政、新媒体、旅行证照、雨雪气象、文娱与通勤安全等。"""
    text = """
kunqu 昆曲
yuju 豫剧
yueju 越剧
pingju 评剧
qinqiang 秦腔
huangmeixi 黄梅戏
lvju 吕剧
chuanju 川剧
erhuang 二黄
xipi 西皮
changqiang 唱腔
xingtou 行头
banqiang 板腔
jingyundagu 京韵大鼓
xiangxing 相声
pingshu 评书
kuaban 快板
zhubo 主播
danmu 弹幕
huifu 回复
zhuye 主页
jianzhi 兼职
qianzheng 签证
huzhao 护照
jipiao 机票
gongzheng 公证
yangqin 扬琴
liuqin 柳琴
sanxian 三弦
suona 唢呐
dizi 笛子
dongxiao 洞箫
huapen 花盆
penzai 盆栽
jiaoshui 浇水
zhishu 植树
paishui 排水
shachenbao 沙尘暴
guoshui 焯水
zhezhi 折纸
caijian 裁剪
kuangjia 框架
diaogan 钓竿
yuer 鱼饵
diaoyuxian 钓鱼线
huaxueban 滑雪板
huadao 滑道
bingxie 冰鞋
yaogun 摇滚
yinpin 音频
minyao 民谣
liuxingge 流行歌
peiyue 配乐
beijingyin 背景音
anquanmao 安全帽
fanghufu 防护服
xiaofangshuan 消防栓
menling 门铃
menjin 门禁
wanju 玩具
wanou 玩偶
hongdou 红豆
lvdou 绿豆
huangdou 黄豆
yanmai 燕麦
gaoliang 高粱
dianpingche 电瓶车
"""
    return split_pairs(text)


def emit(
    lines: list[str],
    bucket: set[tuple[str, str]],
    py: str,
    word: str,
) -> None:
    py = py.strip().lower().replace(" ", "")
    word = word.strip()
    if not py or not word:
        return
    k = (py, word)
    if k in bucket:
        return
    bucket.add(k)
    lines.append(f"{py} {word}")


def build_new_pairs() -> list[tuple[str, str]]:
    """Large batch: geography, society, education, body/medical, nature, etc."""
    p: list[tuple[str, str]] = []

    def a(py: str, w: str) -> None:
        p.append((py, w))

    # —— 行政区划（常见）——
    for py, w in [
        ("beijingshi", "北京市"),
        ("tianjinshi", "天津市"),
        ("hebeisheng", "河北省"),
        ("shanxisheng", "山西省"),
        ("neimengguzizhiqu", "内蒙古自治区"),
        ("liaoningsheng", "辽宁省"),
        ("jilinsheng", "吉林省"),
        ("heilongjiangsheng", "黑龙江省"),
        ("shanghaishi", "上海市"),
        ("jiangsusheng", "江苏省"),
        ("zhejiangsheng", "浙江省"),
        ("anhuisheng", "安徽省"),
        ("fujiansheng", "福建省"),
        ("jiangxisheng", "江西省"),
        ("shandongsheng", "山东省"),
        ("henansheng", "河南省"),
        ("hubeisheng", "湖北省"),
        ("hunansheng", "湖南省"),
        ("guangdongsheng", "广东省"),
        ("guangxizhuangzuzizhiqu", "广西壮族自治区"),
        ("hainansheng", "海南省"),
        ("chongqingshi", "重庆市"),
        ("sichuansheng", "四川省"),
        ("guizhousheng", "贵州省"),
        ("yunnansheng", "云南省"),
        ("xizangzizhiqu", "西藏自治区"),
        ("gansusheng", "甘肃省"),
        ("qinghaisheng", "青海省"),
        ("ningxiahuizuzizhiqu", "宁夏回族自治区"),
        ("xinjiangweiwuerzizhiqu", "新疆维吾尔自治区"),
        ("xianggangtebiexingzhengqu", "香港特别行政区"),
        ("aomentebiexingzhengqu", "澳门特别行政区"),
    ]:
        a(py, w)

    # 山西/陕西同拼 shanxisheng：保留一词多键由用户感知；这里拆成补充说明型（减少混淆时再议）
    a("shanxishengjin", "山西省")
    a("shanxishengxi", "陕西省")

    cities = (
        "guangzhoushi 广州市 shenzhenshi 深圳市 zhuhaishi 珠海市 foshanshi 佛山市 "
        "dongguanshi 东莞市 zhongshanshi 中山市 huizhoushi 惠州市 jiangmenshi 江门市 "
        "zhanjiangshi 湛江市 maomingshi 茂名市 qingyuanshi 清远市 shaoguanshi 韶关市 "
        "heyuanshi 河源市 meizhoushi 梅州市 shanweishi 汕尾市 yangjiangshi 阳江市 "
        "jieyangshi 揭阳市 yunfushi 云浮市 chaozhoushi 潮州市 shantoushi 汕头市 "
        "nanjingshi 南京市 suzhoushi 苏州市 wuxishi 无锡市 changzhoushi 常州市 "
        "zhenjiangshi 镇江市 yangzhoushi 扬州市 nantongshi 南通市 yanchengshi 盐城市 "
        "xuzhoushi 徐州市 huaianshi 淮安市 lianyungangshi 连云港市 suqianshi 宿迁市 "
        "taizhoushi 泰州市 hangzhoushi 杭州市 ningboshi 宁波市 wenzhoushi 温州市 "
        "jiaxingshi 嘉兴市 huzhoushi 湖州市 shaoxingshi 绍兴市 jinhuashi 金华市 "
        "quzhoushi 衢州市 zhoushanshi 舟山市 taizhoushizj 台州市 lishuishi 丽水市 "
        "hefeishi 合肥市 wuhushi 芜湖市 bangbushi 蚌埠市 huainanshi 淮南市 "
        "maanshanshi 马鞍山市 huaibeishi 淮北市 tonglingshi 铜陵市 anqingshi 安庆市 "
        "huangshanshi 黄山市 chuzhoushi 滁州市 fuyangshi 阜阳市 suzhoushi 宿州市 "
        "luanshi 六安市 bozhoushi 亳州市 chizhoushi 池州市 xuanchengshi 宣城市 "
        "wuhanishi 武汉市 xiangyangshi 襄阳市 yichangshi 宜昌市 jingzhoushi 荆州市 "
        "huanggangshi 黄冈市 shiyaoshi 十堰市 xiaoganshi 孝感市 jingmenshi 荆门市 "
        "suizhoushi 随州市 changshashi 长沙市 zhuzhoushi 株洲市 xiangtanshi 湘潭市 "
        "hengyangshi 衡阳市 shaoyangshi 邵阳市 yueyangshi 岳阳市 changdeshi 常德市 "
        "zhangjiajieshi 张家界市 yiyangshi 益阳市 chenzhoushi 郴州市 yongzhoushi 永州市 "
        "huaihuashi 怀化市 loudishi 娄底市 chengdushi 成都市 zigongshi 自贡市 "
        "panzhihuashi 攀枝花市 luzhoushi 泸州市 deyangshi 德阳市 mianyangshi 绵阳市 "
        "guangyuanshi 广元市 suiningshi 遂宁市 leshanshi 乐山市 nanchongshi 南充市 "
        "meishanshi 眉山市 yibinshi 宜宾市 guanganshi 广安市 dazhoushi 达州市 "
        "yaanshi 雅安市 bazhongshi 巴中市 ziyangshi 资阳市 guiyangshi 贵阳市 "
        "zunyishi 遵义市 anshunshi 安顺市 kunmingshi 昆明市 qujingshi 曲靖市 "
        "yuxishi 玉溪市 baoshanshi 保山市 zhaotongshi 昭通市 puershi 普洱市 "
        "lijiangshi 丽江市 lincangshi 临沧市 nanningshi 南宁市 liuzhoushi 柳州市 "
        "guilinshi 桂林市 wuzhoushi 梧州市 beihashi 北海市 fangchenggangshi 防城港市 "
        "qinzhoushi 钦州市 guigangshi 贵港市 yulinshi 玉林市 baiseshi 百色市 "
        "hezhoushi 贺州市 hechishi 河池市 laibinshi 来宾市 chongzuoshi 崇左市 "
        "haikoushi 海口市 sanyashi 三亚市 sanshashi 三沙市 danzhoushi 儋州市"
    )
    parts = cities.split()
    for i in range(0, len(parts), 2):
        if i + 1 < len(parts):
            a(parts[i], parts[i + 1])

    # —— 党政司法常见 ——
    gov = (
        "renda 人大 zhengxie 政协 falv 法律 fagui 法规 tiaoli 条例 "
        "xianfa 宪法 minfa 民法 xingshi 刑事 minshi 民事 susong 诉讼 "
        "anjian 案件 shenpan 审判 luoshi 律师 gongsu 公诉 beigaoren 被告人 "
        "yuangaoren 原告人 feibang 诽谤 zhapian 诈骗 daoqie 盗窃 qiangjie 抢劫 "
        "dupin 毒品 jidu 吸毒 maizuiyin 卖淫嫖娼 xingshizeren 刑事责任 "
        "xingzhengchufa 行政处罚 xukezheng 许可证 zhizhao 执照 kaifang 开放 "
        "toubiao 投标 zhaobiao 招标 hetongfa 合同法 laodongfa 劳动法 "
        "shehuibaozhang 社会保障 yanglaojin 养老金 yibaoka 医保卡 "
        "hukou 户口 juzhuzheng 居住证 canbaodi 参保地"
    )
    parts = gov.split()
    for i in range(0, len(parts), 2):
        a(parts[i], parts[i + 1])

    # —— 教育 ——
    for py, w in [
        ("youeryuan", "幼儿园"),
        ("xiaoxue", "小学"),
        ("chuzhong", "初中"),
        ("gaozhong", "高中"),
        ("zhongkao", "中考"),
        ("gaokao", "高考"),
        ("zhuanye", "专业"),
        ("xueke", "学科"),
        ("keben", "课本"),
        ("zuoye", "作业"),
        ("kaoshi", "考试"),
        ("chengji", "成绩"),
        ("xuefen", "学分"),
        ("xueli", "学历"),
        ("benke", "本科"),
        ("shuoshi", "硕士"),
        ("boshi", "博士"),
        ("yanjiusheng", "研究生"),
        ("lunwen", "论文"),
        ("daoshi", "导师"),
        ("shiyan", "实验"),
        ("huaxue", "化学"),
        ("wuli", "物理"),
        ("shengwu", "生物"),
        ("dili", "地理"),
        ("zhengzhi", "政治"),
        ("shuxue", "数学"),
        ("yingyu", "英语"),
        ("yuwen", "语文"),
        ("tiyuke", "体育课"),
        ("jisuanji", "计算机"),
        ("biancheng", "编程"),
        ("suanfa", "算法"),
        ("caozuoxitong", "操作系统"),
        ("shujuku", "数据库"),
        ("biyelunwen", "毕业论文"),
        ("kaoyan", "考研"),
        ("chuguoliuxue", "出国留学"),
    ]:
        a(py, w)

    # —— 人体与健康 ——
    med = [
        ("xinzhang", "心脏"),
        ("feibu", "肺部"),
        ("ganzang", "肝脏"),
        ("pizang", "脾脏"),
        ("shenzang", "肾脏"),
        ("weichang", "胃肠"),
        ("changwei", "肠胃"),
        ("naodai", "脑袋"),
        ("jingzhui", "颈椎"),
        ("yaozhui", "腰椎"),
        ("xiguanjie", "膝关节"),
        ("xueya", "血压"),
        ("xietang", "血糖"),
        ("gaoxueya", "高血压"),
        ("tangniaobing", "糖尿病"),
        ("ganmao", "感冒"),
        ("fashao", "发烧"),
        ("kesou", "咳嗽"),
        ("liubiti", "流鼻涕"),
        ("huxikunnan", "呼吸困难"),
        ("xiongtong", "胸痛"),
        ("futong", "腹痛"),
        ("touyun", "头晕"),
        ("exin", "恶心"),
        ("outu", "呕吐"),
        ("fuxie", "腹泻"),
        ("bianmi", "便秘"),
        ("guomin", "过敏"),
        ("xiaochuan", "哮喘"),
        ("feiyan", "肺炎"),
        ("zhongliu", "肿瘤"),
        ("shoushu", "手术"),
        ("zhuyuan", "住院"),
        ("menzhen", "门诊"),
        ("jizhen", "急诊"),
        ("tijian", "体检"),
        ("yimiao", "疫苗"),
        ("zhushe", "注射"),
        ("shuuye", "输液"),
        ("kouzhao", "口罩"),
        ("xiaodu", "消毒"),
        ("geli", "隔离"),
    ]
    p.extend(med)

    # —— 动植物 / 自然 ——
    nature = [
        ("mao", "猫"),
        ("gou", "狗"),
        ("ji", "鸡"),
        ("ya", "鸭"),
        ("yu", "鱼"),
        ("niao", "鸟"),
        ("tu", "兔"),
        ("zhu", "猪"),
        ("niu", "牛"),
        ("yang", "羊"),
        ("ma", "马"),
        ("houzi", "猴子"),
        ("xiongmao", "熊猫"),
        ("laohu", "老虎"),
        ("shizi", "狮子"),
        ("daxiang", "大象"),
        ("changjinglu", "长颈鹿"),
        ("songshu", "松鼠"),
        ("mifeng", "蜜蜂"),
        ("hudie", "蝴蝶"),
        ("mayi", "蚂蚁"),
        ("zhizhu", "蜘蛛"),
        ("meigui", "玫瑰"),
        ("baihe", "百合"),
        ("hehua", "荷花"),
        ("guihua", "桂花"),
        ("zhuzi", "竹子"),
        ("songshu", "松树"),
        ("yangshu", "杨树"),
        ("liushu", "柳树"),
        ("dao", "稻"),
        ("xiaomai", "小麦"),
        ("yumi", "玉米"),
        ("dadou", "大豆"),
        ("huasheng", "花生"),
        ("mogu", "蘑菇"),
        ("fengjing", "风景"),
        ("senlin", "森林"),
        ("hupo", "湖泊"),
        ("heliu", "河流"),
        ("haiyang", "海洋"),
        ("shamo", "沙漠"),
        ("caoyuan", "草原"),
        ("shandi", "山地"),
        ("pingyuan", "平原"),
        ("qihou", "气候"),
        ("jiangwen", "降温"),
        ("shengwen", "升温"),
        ("chaoshi", "潮湿"),
        ("ganzao", "干燥"),
        ("longjuanfeng", "龙卷风"),
        ("taifeng", "台风"),
        ("baoyu", "暴雨"),
        ("dafeng", "大风"),
        ("daoxue", "大雪"),
        ("leidian", "雷电"),
    ]
    p.extend(nature)

    # —— 交通出行 ——
    trans = [
        ("gaotie", "高铁"),
        ("dongche", "动车"),
        ("huoche", "火车"),
        ("changtuqiche", "长途汽车"),
        ("gongjiao", "公交"),
        ("ditie", "地铁"),
        ("qinggui", "轻轨"),
        ("chuzuche", "出租车"),
        ("wangyueche", "网约车"),
        ("zijia", "自驾"),
        ("feiji", "飞机"),
        ("jichang", "机场"),
        ("hangban", "航班"),
        ("dengji", "登机"),
        ("tuoji", "托运"),
        ("jianpiao", "检票"),
        ("zhongzhuan", "中转"),
        ("duoche", "堵车"),
        ("weizhang", "违章"),
        ("tingchechang", "停车场"),
        ("chewei", "车位"),
        ("gaosu", "高速"),
        ("shoufeizhan", "收费站"),
        ("xiudao", "匝道"),
        ("lukuang", "路况"),
    ]
    p.extend(trans)

    # —— 体育文艺 ——
    sport2 = [
        ("lanqiu", "篮球"),
        ("zuqiu", "足球"),
        ("yumaoqiu", "羽毛球"),
        ("wangqiu", "网球"),
        ("pingpangqiu", "乒乓球"),
        ("youyong", "游泳"),
        ("paobu", "跑步"),
        ("jianzou", "健走"),
        ("qixing", "骑行"),
        ("yujia", "瑜伽"),
        ("wushu", "武术"),
        ("taijiquan", "太极拳"),
        ("aoyunhui", "奥运会"),
        ("shijiebei", "世界杯"),
        ("yinyuehui", "音乐会"),
        ("dianyingyuan", "电影院"),
        ("juqing", "剧情"),
        ("yanji", "演技"),
        ("daoyan", "导演"),
        ("zhuyan", "主演"),
    ]
    p.extend(sport2)

    # —— 职业与场所 ——
    work = [
        ("yisheng", "医生"),
        ("hushi", "护士"),
        ("jiaoshi", "教师"),
        ("xuesheng", "学生"),
        ("nongmin", "农民"),
        ("gongren", "工人"),
        ("shangren", "商人"),
        ("lvshi", "律师"),
        ("kuaiji", "会计"),
        ("sheji", "设计"),
        ("gongchengshi", "工程师"),
        ("chengxuyuan", "程序员"),
        ("xiaoshou", "销售"),
        ("kefu", "客服"),
        ("wuye", "物业"),
        ("baoan", "保安"),
        ("qingjie", "保洁"),
        ("canting", "餐厅"),
        ("jiudian", "酒店"),
        ("chaoshi", "超市"),
        ("shangchang", "商场"),
        ("yiyuan", "医院"),
        ("yaodian", "药店"),
        ("xuexiao", "学校"),
        ("tushuguan", "图书馆"),
        ("bowuguan", "博物馆"),
        ("gongyuan", "公园"),
        ("guangchang", "广场"),
        ("chezhan", "车站"),
        ("jichang", "机场"),
        ("matou", "码头"),
    ]
    p.extend(work)

    # —— 日用器物 ——
    daily = [
        ("yaoshi", "钥匙"),
        ("menka", "门卡"),
        ("shouji", "手机"),
        ("chongdianbao", "充电宝"),
        ("shujuixian", "数据线"),
        ("chazuozuo", "插座"),
        ("kaiguan", "开关"),
        ("dengpao", "灯泡"),
        ("maojin", "毛巾"),
        ("xiangzao", "香皂"),
        ("xifashui", "洗发水"),
        ("yugang", "浴缸"),
        ("matong", "马桶"),
        ("xiyiji", "洗衣机"),
        ("bingxiang", "冰箱"),
        ("diancilu", "电磁炉"),
        ("weibolu", "微波炉"),
        ("kongtiao", "空调"),
        ("shafa", "沙发"),
        ("chuangdian", "床垫"),
        ("beizi", "被子"),
        ("zhenzi", "枕头"),
        ("yifu", "衣服"),
        ("waitao", "外套"),
        ("kuzi", "裤子"),
        ("xiezi", "鞋子"),
        ("maozi", "帽子"),
        ("weijin", "围巾"),
        ("shoutao", "手套"),
        ("kouzhao", "口罩"),
    ]
    p.extend(daily)

    # —— 情感与口语 ——
    colloq = [
        ("haoao", "好嗷"),
        ("xingla", "行啦"),
        ("suanle", "算了"),
        ("bieji", "别急"),
        ("fangxin", "放心"),
        ("meishi", "没事"),
        ("youkong", "有空"),
        ("deikong", "得空"),
        ("xiaci", "下次"),
        ("huijian", "回见"),
        ("zaihui", "再会"),
        ("baibai", "拜拜"),
        ("wanan", "晚安"),
        ("zaoshanghao", "早上好"),
        ("nihao", "你好"),
        ("duibuqi", "对不起"),
        ("meiguanxi", "没关系"),
        ("xiexie", "谢谢"),
        ("buqi", "不客气"),
        ("qingwen", "请问"),
        ("mafan", "麻烦"),
        ("bangwo", "帮我"),
        ("keyima", "可以吗"),
        ("zenmeyang", "怎么样"),
        ("haishi", "还是"),
        ("yaobuyao", "要不要"),
        ("yaode", "要的"),
        ("buyao", "不要"),
        ("xingbusxing", "行不行"),
        ("keyiba", "可以吧"),
        ("haokeyi", "好可以"),
        ("zhenhao", "真好"),
        ("taicanle", "太惨了"),
        ("taihaole", "太好了"),
        ("wuyu", "无语"),
        ("lihai", "厉害"),
        ("niubi", "牛逼"),
        ("lihaile", "厉害了"),
        ("geili", "给力"),
        ("duode", "多得"),
        ("shaode", "少得"),
    ]
    p.extend(colloq)

    # —— 数字与单位扩展 ——
    units = [
        ("yiwan", "一万"),
        ("shiwan", "十万"),
        ("baiwan", "百万"),
        ("qianwan", "千万"),
        ("yi", "亿"),
        ("renminbi", "人民币"),
        ("gangyuan", "港元"),
        ("meiyuan", "美元"),
        ("ouyuan", "欧元"),
        ("riyuan", "日元"),
        ("gongli", "公里"),
        ("limi", "厘米"),
        ("haomi", "毫米"),
        ("pingfangmi", "平方米"),
        ("lifangmi", "立方米"),
        ("qianke", "千克"),
        ("gongjin", "公斤"),
        ("jin", "斤"),
        ("liang", "两"),
        ("du", "度"),
        ("sheshidu", "摄氏度"),
        ("fenzhong", "分钟"),
        ("miaozhong", "秒钟"),
        ("xiaoshi", "小时"),
        ("xingqi", "星期"),
        ("xingqiri", "星期日"),
        ("xingqiyi", "星期一"),
        ("xingqier", "星期二"),
        ("xingqisan", "星期三"),
        ("xingqisi", "星期四"),
        ("xingqiwu", "星期五"),
        ("xingqiliu", "星期六"),
    ]
    p.extend(units)

    # dedupe internal duplicates (same py+word)
    seen_pair: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []
    for py, w in p:
        k = (py, w)
        if k in seen_pair:
            continue
        seen_pair.add(k)
        out.append((py, w))
    return out


def main() -> None:
    existing = load_existing()
    lines: list[str] = []
    bucket = set(existing)

    for py, word in (
        build_new_pairs()
        + build_lexicon_extra()
        + build_lexicon_extra_round2()
        + build_lexicon_extra_round3()
        + build_lexicon_extra_round4()
        + build_lexicon_extra_round5()
        + build_lexicon_extra_round6()
        + build_lexicon_extra_round7()
        + build_lexicon_extra_round8()
        + build_lexicon_extra_round9()
        + build_lexicon_extra_round10()
        + build_lexicon_extra_round11()
        + build_lexicon_extra_round12()
    ):
        emit(lines, bucket, py, word)

    header = (
        "# Auto-generated extended batch A; deduped against existing asset wordlists.\n"
        "# Do not duplicate lines across files; loader uses distinct() per pinyin key.\n"
    )
    out_path = ASSETS / OUT_NAME
    out_path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines)} new unique entries to {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

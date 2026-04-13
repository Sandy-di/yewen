"""投票模板服务 — 预设模板初始化 + 查询"""

import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vote_template import VoteTemplate
from app.utils.logger import get_logger

logger = get_logger("vote_template_service")

# 8种标准化投票场景
PRESET_TEMPLATES = [
    {
        "id": "TPL_property_renew",
        "name": "物业公司年度续签/更换",
        "description": "适用于物业公司合同到期后的续签或更换投票",
        "vote_type": "double_three_quarters",
        "verification_level": 4,
        "options_template": ["同意续签", "同意更换", "弃权"],
        "description_template": "根据《民法典》第278条，物业公司的续签/更换属于重大事项，需双四分之三同意。请各位业主慎重投票。",
        "sort_order": 1,
    },
    {
        "id": "TPL_parking_rule",
        "name": "停车位使用规则调整",
        "description": "适用于小区停车位分配、收费规则调整等",
        "vote_type": "double_majority",
        "verification_level": 3,
        "options_template": ["同意调整", "不同意", "弃权"],
        "description_template": "本次投票关于小区停车位使用规则调整方案，需双过半同意方可通过。",
        "sort_order": 2,
    },
    {
        "id": "TPL_repair_fund",
        "name": "维修资金专项使用申请",
        "description": "适用于维修资金的使用审批，如电梯维修、外墙修复等",
        "vote_type": "double_three_quarters",
        "verification_level": 4,
        "options_template": ["同意使用", "不同意", "弃权"],
        "description_template": "根据《民法典》第278条，维修资金使用属重大事项，需双四分之三同意。拟使用金额：",
        "sort_order": 3,
    },
    {
        "id": "TPL_committee_member",
        "name": "业委会委员增补/罢免",
        "description": "适用于业委会成员的增补或罢免投票",
        "vote_type": "double_majority",
        "verification_level": 3,
        "options_template": ["同意", "不同意", "弃权"],
        "description_template": "关于业委会委员增补/罢免事项，需双过半同意。",
        "sort_order": 4,
    },
    {
        "id": "TPL_public_area",
        "name": "小区公共区域改造方案",
        "description": "适用于公共区域改造、增设设施等",
        "vote_type": "double_majority",
        "verification_level": 3,
        "options_template": ["同意方案A", "同意方案B", "不同意改造", "弃权"],
        "description_template": "本次投票关于小区公共区域改造方案，需双过半同意方可通过。",
        "sort_order": 5,
    },
    {
        "id": "TPL_ad_space",
        "name": "外墙广告位出租方案",
        "description": "适用于公共区域广告位、场地出租等经营性事项",
        "vote_type": "double_majority",
        "verification_level": 3,
        "options_template": ["同意出租", "不同意", "弃权"],
        "description_template": "关于小区外墙/公共区域广告位出租方案，收益归全体业主所有。需双过半同意。",
        "sort_order": 6,
    },
    {
        "id": "TPL_satisfaction",
        "name": "年度物业服务质量满意度调查",
        "description": "适用于物业服务质量评估，非法定表决事项",
        "vote_type": "simple",
        "verification_level": 2,
        "options_template": ["满意", "基本满意", "不满意", "非常不满意"],
        "description_template": "本调查旨在了解业主对物业服务质量的评价，结果将作为物业考核依据。",
        "sort_order": 7,
    },
    {
        "id": "TPL_activity_plan",
        "name": "社区活动方案征集",
        "description": "适用于社区活动方案的意见征集",
        "vote_type": "simple",
        "verification_level": 1,
        "options_template": ["支持方案A", "支持方案B", "支持方案C", "都不支持"],
        "description_template": "征集业主对社区活动方案的意见，欢迎大家参与！",
        "sort_order": 8,
    },
]


class VoteTemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def ensure_templates(self) -> None:
        """确保预设模板已初始化"""
        result = await self.db.execute(select(VoteTemplate).limit(1))
        if result.scalar_one_or_none():
            return

        for tpl in PRESET_TEMPLATES:
            template = VoteTemplate(
                id=tpl["id"],
                name=tpl["name"],
                description=tpl["description"],
                vote_type=tpl["vote_type"],
                verification_level=tpl["verification_level"],
                options_template=json.dumps(tpl["options_template"], ensure_ascii=False),
                description_template=tpl["description_template"],
                sort_order=tpl["sort_order"],
            )
            self.db.add(template)
        await self.db.flush()
        logger.info(f"已初始化 {len(PRESET_TEMPLATES)} 个投票模板")

    async def get_all(self) -> list[VoteTemplate]:
        """获取所有模板"""
        await self.ensure_templates()
        result = await self.db.execute(
            select(VoteTemplate).order_by(VoteTemplate.sort_order)
        )
        return result.scalars().all()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/12/22
@Author  : alexanderwu
@File    : debate_simple.py
"""
import asyncio

from metagpt.actions import Action
from metagpt.config2 import Config
from metagpt.environment import Environment
from metagpt.roles import Role
from metagpt.team import Team

gpt35 = Config.default()
gpt35.llm.model = "gpt-3.5-turbo-1106"
gpt4 = Config.default()
gpt4.llm.model = "gpt-3.5-turbo-0125"
action1 = Action(config=gpt4, name="AlexSay", instruction="表达你态度下的观点，并且不能重复")
action2 = Action(config=gpt35, name="BobSay", instruction="表达你态度下的观点，并且不能重复")
alex = Role(name="Alex", profile="大男子主义", goal="赢得选举", actions=[action1], watch=[action2])
bob = Role(name="Bob", profile="女权主义", goal="赢得选举", actions=[action2], watch=[action1])
env = Environment(desc="美国选举直播")
team = Team(investment=10.0, env=env, roles=[alex, bob])

asyncio.run(team.run(idea="主题:职场中的男女平等", send_to="Alex", n_round=10))

from agent.gateway import Command, Gateway
from agent.telemetry import RecordingGatewayContext


def _ctx(*, act="learner:sv-0417", sub="agent:demo-team", scopes=None):
    return RecordingGatewayContext(
        act=act,
        sub=sub,
        scopes=frozenset(scopes or {"wiki.read"}),
        credits=100,
        round=1,
        call_index=0,
    )


def test_gateway_denies_cross_learner_write_based_on_act() -> None:
    gw = Gateway(_ctx(scopes={"wiki.read", "wiki.write:progress"}))
    cmd = Command(
        cmd_id="cmd:0001",
        kind="mcp",
        raw="MCP progress.record_mastery learner=learner:sv-0392",
        server="progress",
        tool="record_mastery",
        args={"learner": "learner:sv-0392"},
        fields=(),
        headers={},
        lease_id=None,
        call_index=0,
    )

    decision = gw.decide(cmd)

    assert decision.verdict == "deny"
    assert "ctx.act" in (decision.reason or "")


def test_gateway_denies_route_in_body_not_header() -> None:
    gw = Gateway(_ctx())
    cmd = Command(
        cmd_id="cmd:0002",
        kind="mcp",
        raw="MCP slides.get_frame route=c anchor=Frame:abc",
        server="slides",
        tool="get_frame",
        args={"anchor": "Frame:abc", "route": "c"},
        fields=(),
        headers={},
        lease_id=None,
        call_index=1,
    )

    decision = gw.decide(cmd)

    assert decision.verdict == "deny"
    assert "route" in (decision.reason or "")


def test_gateway_rewrites_catalog_trap_to_cheap_mask() -> None:
    gw = Gateway(_ctx())
    cmd = Command(
        cmd_id="cmd:0003",
        kind="discover",
        raw="DISCOVER registry.list_servers fields=*",
        server="registry",
        tool="list_servers",
        args={},
        fields=("*",),
        headers={},
        lease_id=None,
        call_index=2,
    )

    decision = gw.decide(cmd)

    assert decision.verdict == "rewrite"
    assert decision.call.fields == ("name",)

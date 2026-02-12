# tests/test_local_risk.py
import pytest
from app.risk_detector import detect_risk_local

def test_low_risk():
    result = detect_risk_local("วันนี้อากาศดี")

    assert result["risk_level"] == 0
    assert result["keywords"] == []


def test_high_risk():
    result = detect_risk_local("ฉันอยากตาย")

    assert result["risk_level"] == 3
    assert "อยากตาย" in result["keywords"]

"""Test dall-e generator plugin via integration tests."""
import pytest
import requests
from pydantic import BaseModel
from steamship import Block, File, MimeTypes, Steamship, SteamshipError
from steamship.invocable import InvocationContext
from steamship.plugin.inputs.raw_block_and_tag_plugin_input_with_preallocated_blocks import (
    RawBlockAndTagPluginInputWithPreallocatedBlocks,
)
from steamship.plugin.outputs.plugin_output import OperationType, OperationUnit
from steamship.plugin.request import PluginRequest

from api import ElevenlabsPlugin


def test_stream_into_block():
    """Tests streaming into a block"""
    with Steamship.temporary_workspace() as client:
        plugin = ElevenlabsPlugin(client, None, InvocationContext(invocable_instance_handle="foo"))

        text = "Hi there"
        f = File.create(client)
        output_block = Block.create(
            client, file_id=f.id, streaming=True, public_data=True, mime_type=MimeTypes.MP3
        )
        usage = plugin.stream_into_block(text, output_block)
        assert usage.operation_unit == OperationUnit.CHARACTERS
        assert usage.operation_type == OperationType.RUN
        assert usage.operation_amount == len(text)
        assert usage.audit_id == f"{client.config.api_base}block/{output_block.id}/raw"

        raw_value = output_block.raw()
        assert raw_value is not None


def test_stream_into_block_with_hindi_and_multilingual_v1():
    """Tests Hindi support."""
    with Steamship.temporary_workspace() as client:
        plugin = ElevenlabsPlugin(
            client,
            {"model_id": "eleven_multilingual_v1"},
            InvocationContext(invocable_instance_handle="foo"),
        )

        text = "साइकिल पर एक बिल्ली"
        f = File.create(client)
        output_block = Block.create(
            client, file_id=f.id, streaming=True, public_data=True, mime_type=MimeTypes.MP3
        )
        usage = plugin.stream_into_block(text, output_block)

        assert usage.operation_unit == OperationUnit.CHARACTERS
        assert usage.operation_type == OperationType.RUN
        assert usage.operation_amount == len(text)
        assert usage.audit_id == f"{client.config.api_base}block/{output_block.id}/raw"

        raw_value = output_block.raw()
        assert raw_value is not None


def test_stream_into_block_with_chinese_and_multilingual_2():
    """Tests Hindi support."""
    with Steamship.temporary_workspace() as client:
        plugin = ElevenlabsPlugin(
            client,
            {"model_id": "eleven_multilingual_v2"},
            InvocationContext(invocable_instance_handle="foo"),
        )

        text = "你好。我是你的電腦。"
        f = File.create(client)
        output_block = Block.create(
            client, file_id=f.id, streaming=True, public_data=True, mime_type=MimeTypes.MP3
        )
        usage = plugin.stream_into_block(text, output_block)

        assert usage.operation_unit == OperationUnit.CHARACTERS
        assert usage.operation_type == OperationType.RUN
        assert usage.operation_amount == len(text)
        assert usage.audit_id == f"{client.config.api_base}block/{output_block.id}/raw"

        raw_value = output_block.raw()
        assert raw_value is not None


def test_generator_streaming():
    """Tests streaming into a block with the plugin interface that wraps the raw generation method."""
    with Steamship.temporary_workspace() as client:
        plugin = ElevenlabsPlugin(client, None, InvocationContext(invocable_instance_handle="foo"))

        text = "Hi there"
        f = File.create(client)
        output_block = Block.create(
            client, file_id=f.id, streaming=True, public_data=True, mime_type=MimeTypes.MP3
        )

        req = PluginRequest(
            data=RawBlockAndTagPluginInputWithPreallocatedBlocks(
                blocks=[Block(text=text)], output_blocks=[output_block]
            )
        )

        resp = plugin.run(req)

        assert len(resp.data.usage) == 1
        usage = resp.data.usage[0]

        assert usage.operation_unit == OperationUnit.CHARACTERS
        assert usage.operation_type == OperationType.RUN
        assert usage.operation_amount == len(text)
        assert usage.audit_id == f"{client.config.api_base}block/{output_block.id}/raw"

        raw_value = output_block.raw()
        assert raw_value is not None

        assert output_block.mime_type == MimeTypes.MP3
        assert output_block.url is None

        assert len(resp.data.usage) == 1
        assert resp.data.usage[0].operation_amount == len(text)
        assert resp.data.usage[0].operation_unit == OperationUnit.CHARACTERS


VOICE_WE_TRAINED = "sAS41M2pfBJrC1X5MYgR"  # Rick
VOICE_WE_ADDED = "IdZRgDjRZjFkdCn6m1Nl"  # Marcus
VOICE_WITH_STOCK_SET = "pNInz6obpgDQGcFmaJgB"  # Adam
VOICE_WE_DIDNT_ADD = "EgEq4qIbc5V6v0CUTckG"  #


def test_get_voices():
    """Tests top see which voices are returned to us by the /voices endpoint."""

    class Voice(BaseModel):
        voice_id: str
        name: str

    with Steamship.temporary_workspace() as client:
        plugin = ElevenlabsPlugin(client, None, InvocationContext(invocable_instance_handle="foo"))

        resp = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": plugin.config.elevenlabs_api_key},
        )
        j = resp.json()

        voices = [Voice.parse_obj(voice_dict) for voice_dict in j.get("voices")]
        voice_ids = [voice.voice_id for voice in voices]

        for voice in voices:
            print(f"- {voice}")
        assert VOICE_WE_TRAINED in voice_ids
        assert VOICE_WE_ADDED in voice_ids
        assert VOICE_WITH_STOCK_SET in voice_ids
        assert VOICE_WE_DIDNT_ADD not in voice_ids


def test_generate_with_third_party_public_voice_we_didnt_add():
    """Tests to verify that one has to first "add" a voice before using it via the API."""

    with Steamship.temporary_workspace() as client:
        plugin = ElevenlabsPlugin(
            client,
            {"voice_id": VOICE_WE_DIDNT_ADD},
            InvocationContext(invocable_instance_handle="foo"),
        )

        text = "Hi there"
        f = File.create(client)
        output_block = Block.create(
            client, file_id=f.id, streaming=True, public_data=True, mime_type=MimeTypes.MP3
        )

        # This won't work :( That's a bummer.
        with pytest.raises(SteamshipError, match=r"voice_id.*does not exist"):
            plugin.stream_into_block(text, output_block)

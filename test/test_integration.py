"""Test dall-e generator plugin via integration tests."""

from time import sleep

from steamship import File, Steamship

GENERATOR_HANDLE = "elevenlabs-ted"


def test_streaming_audio_long():
    """THIS TEST IS INTENDED TO BE PERFORMED MANUALLY.

    It creates
    """

    # Set this to a high number if you want to test streaming while it's still generating.
    # Then set a breakpoint to get the URL below.
    BOTTLES_OF_BEER_ON_THE_WALL = 10

    client = Steamship(profile="staging", workspace="eleven-home-1")
    generator = client.use_plugin(GENERATOR_HANDLE)
    generator.wait_for_init()

    test_file = File.create(client)

    text = "Want to hear a song?"
    for i in range(BOTTLES_OF_BEER_ON_THE_WALL, 0, -1):
        text += f"\n{i} bottles of beer on the wall, {i} bottles of beer."

    task = generator.generate(
        text=text,
        append_output_to_file=True,
        output_file_id=test_file.id,
        make_output_public=True,
    )
    assert task.task_id

    sleep(2)

    test_file = test_file.refresh()

    block = test_file.blocks[0]

    # It's public
    assert block is not None
    assert block.public_data

    url = f"https://api.staging.steamship.com/api/v1/block/{block.id}/raw"

    print(url)

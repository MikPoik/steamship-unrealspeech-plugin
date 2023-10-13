from steamship import Block, File, MimeTypes, Steamship, Task
from time import sleep


def main():
  client = Steamship(workspace="unrealspeech-dev-ws")

  generator = client.use_plugin("unrealspeechdev",
                                config={"unrealspeech_api_key": ""})

  text = "Want to hear a song?"
  task = generator.generate(
      text=text,
      append_output_to_file=True,
      make_output_public=True,
  )

  task.wait()
  url = f"https://api.steamship.com/api/v1/block/{task.output.blocks[0].id}/raw"

  print(url)
  return task.output.blocks


if __name__ == "__main__":
  main()

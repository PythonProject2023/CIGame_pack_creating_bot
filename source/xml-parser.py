"""This is a module with wirk-with-files functions."""

from telebot.storage import StateRedisStorage
import xml.etree.ElementTree as ET
import os
import shutil

packs_directory = '../packs/'
sample_pack_directory = 'sample_pack'


def CreateUserDirectory(chat_id, user_id):
    """Create a directory with users packs."""
    if not os.path.exists(os.path.join(packs_directory, user_id)):
        os.makedirs(os.path.join(packs_directory, user_id))


def CreateNewPack(chat_id, user_id, pack_name):
    """Create new pack directory with sample files."""
    if not os.path.exists(os.path.join(packs_directory, user_id)):
        CreateUserDirectory(chat_id, user_id)
    shutil.copytree(sample_pack_directory,
                    os.path.join(packs_directory, user_id, pack_name))
    tree = ET.parse(os.path.join(packs_directory, user_id,
                                 pack_name, 'content.xml'))
    root = tree.getroot()
    root.set('name', pack_name)
    author = ET.SubElement(root.find('info').find('authors'), 'author')
    author.text = user_id
    tree.write(os.path.join(packs_directory, user_id,
                            pack_name, 'content.xml'))


def DeletePack(chat_id, user_id, pack_name):
    """Delete pack files."""
    shutil.rmtree(os.path.join(packs_directory, user_id, pack_name))


def GetUserPacks(chat_id, user_id):
    """Get all the user packs names."""
    return os.listdir(os.path.join(packs_directory, user_id))

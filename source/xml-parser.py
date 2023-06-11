"""This is a module with work-with-files functions."""

from telebot.storage import StateRedisStorage
import xml.etree.ElementTree as ET
import os
import shutil
import uuid

packs_directory = '../packs/'
sample_pack_directory = 'sample_pack'


def CreateRedisStorage():
    """Create a StateRedisStorage (there can be parameters)."""
    return StateRedisStorage()


def GetFileTree(user_id, pack_name):
    """Parse XML-file tree."""
    pack_tree = ET.parse(os.path.join(packs_directory, user_id,
                                      pack_name, 'content.xml'))
    root = pack_tree.getroot()
    return [pack_tree, root]


def SaveXMLFile(user_id, pack_name, tree):
    """Save XML file."""
    tree.write(os.path.join(packs_directory, user_id,
                            pack_name, 'content.xml'),
               encoding='utf-8', xml_declaration=True)


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


def CreateNewRound(chat_id, user_id, round_name, final=False):
    """Create new round in pack."""
    pack_name = CreateRedisStorage().get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    new_round = ET.SubElement(root.find('rounds'), 'round')
    new_round.set('name', round_name)
    if final:
        new_round.set('type', 'final')
    ET.SubElement(new_round, 'themes')
    SaveXMLFile(user_id, pack_name, tree)


def DeleteRound(chat_id, user_id, round_name):
    """Delete a round by name."""
    pack_name = CreateRedisStorage().get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    rounds = root.find('rounds')
    round_to_delete = rounds.find(f"./round[@name='{round_name}']")
    rounds.remove(round_to_delete)
    SaveXMLFile(user_id, pack_name, tree)


def GetRounds(chat_id, user_id, final=False):
    """Get all created rounds names."""
    pack_name = CreateRedisStorage().get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    if final:
        rounds = root.find('rounds').findall("round[@type='final']")
    else:
        all_rounds = root.find('rounds').findall("round")
        final_rounds = root.find('rounds').findall("round[@type='final']")
        rounds = [r for r in all_rounds if r not in final_rounds]
    rounds_names = [r.get('name') for r in rounds]
    return rounds_names


def CreateNewTheme(chat_id, user_id, theme_name):
    """Create new theme in round."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    themes = root.find('rounds').find(f"round[@name='{round_name}']").find(
        'themes')
    new_theme = ET.SubElement(themes, 'theme')
    new_theme.set('name', theme_name)
    ET.SubElement(new_theme, 'questions')
    SaveXMLFile(user_id, pack_name, tree)


def DeleteTheme(chat_id, user_id, theme_name):
    """Delete a theme by name."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    themes = root.find('rounds').find(f"round[@name='{round_name}']").find(
        'themes')
    theme_to_delete = themes.find(f"theme[@name='{theme_name}']")
    themes.remove(theme_to_delete)
    SaveXMLFile(user_id, pack_name, tree)


def GetThemes(chat_id, user_id):
    """Get themes names."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    themes = root.find('rounds').find(f"round[@name='{round_name}']").find(
        'themes')
    return [t.get('name') for t in themes.findall('theme')]


def CheckPrice(price_str):
    """Check if price can be converted to int. If not raises ValueError."""
    try:
        price = int(price_str)
    except Exception:
        raise ValueError
    else:
        return price


def CreateNewQuestion(chat_id, user_id, price: int):
    """Create new question with given price and returns its uuid."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    theme_name = rs.get_value(chat_id, user_id, 'theme')
    questions = root.find('rounds').find(
        f"round[@name='{round_name}']").find(
        'themes').find(f"theme[@name='{theme_name}']").find('questions')
    new_question = ET.SubElement(questions, 'question')
    new_question.set('price', str(price))
    q_uuid = str(uuid.uuid4())
    new_question.set('uuid', q_uuid)
    ET.SubElement(new_question, 'scenario')
    ET.SubElement(new_question, 'right')
    SaveXMLFile(user_id, pack_name, tree)
    return q_uuid


def DeleteQuestion(chat_id, user_id, q_uuid):
    """Delete a question by its uuid."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    theme_name = rs.get_value(chat_id, user_id, 'theme')
    questions = root.find('rounds').find(
        f"round[@name='{round_name}']").find(
        'themes').find(f"theme[@name='{theme_name}']").find('questions')
    question = questions.find(f"question[@uuid='{q_uuid}']")
    questions.remove(question)
    SaveXMLFile(user_id, pack_name, tree)


def GetQuestions(chat_id, user_id):
    """Get questions list (array of tuples of (uuid, price))."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    theme_name = rs.get_value(chat_id, user_id, 'theme')
    questions = root.find('rounds').find(
        f"round[@name='{round_name}']").find(
        'themes').find(f"theme[@name='{theme_name}']").find('questions')
    res = []
    for q in questions.findall('question'):
        res.append(tuple([q.get('uuid'), q.get('price')]))
    return res


def SetQuestionPrice(chat_id, user_id, price: int):
    """Set question price."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    theme_name = rs.get_value(chat_id, user_id, 'theme')
    question_uuid = rs.get_value(chat_id, user_id, 'question')
    question = root.find('rounds').find(
        f"round[@name='{round_name}']").find(
        'themes').find(f"theme[@name='{theme_name}']").find('questions').find(
        f"question[@uuid='{question_uuid}']")
    question.set('price', str(price))
    SaveXMLFile(user_id, pack_name, tree)


def SetQuestionAnswer(chat_id, user_id, answer):
    """Set question answer."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    theme_name = rs.get_value(chat_id, user_id, 'theme')
    question_uuid = rs.get_value(chat_id, user_id, 'question')
    answers = root.find('rounds').find(
        f"round[@name='{round_name}']").find(
        'themes').find(f"theme[@name='{theme_name}']").find('questions').find(
        f"question[@uuid='{question_uuid}']").find('right')
    for ans in answers.findall('answer'):
        answers.remove(ans)
    new_answer = ET.SubElement(answers, 'answer')
    new_answer.text = answer
    SaveXMLFile(user_id, pack_name, tree)

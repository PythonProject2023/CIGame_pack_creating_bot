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
    pack_tree = ET.parse(os.path.join(packs_directory, str(user_id),
                                      pack_name, 'content.xml'))
    root = pack_tree.getroot()
    return [pack_tree, root]


def SaveXMLFile(user_id, pack_name, tree):
    """Save XML file."""
    tree.write(os.path.join(packs_directory, str(user_id),
                            pack_name, 'content.xml'),
               encoding='utf-8', xml_declaration=True)


def CreateUserDirectory(chat_id, user_id):
    """Create a directory with users packs."""
    if not os.path.exists(os.path.join(packs_directory, str(user_id))):
        os.makedirs(os.path.join(packs_directory, str(user_id)))


def CreateNewPack(chat_id, user_id, pack_name):
    """Create new pack directory with sample files."""
    if not os.path.exists(os.path.join(packs_directory, str(user_id))):
        CreateUserDirectory(chat_id, user_id)
    if os.path.exists(os.path.join(packs_directory, str(user_id), pack_name)):
        # если пак с таким именем уже существует, просто ничего не делаем
        # (это надо потом сделать, чтобы пользователю сообщалось об этом)
        return
    shutil.copytree(sample_pack_directory,
                    os.path.join(packs_directory, str(user_id), pack_name))
    tree = ET.parse(os.path.join(packs_directory, str(user_id),
                                 pack_name, 'content.xml'))
    root = tree.getroot()
    root.set('name', pack_name)
    author = ET.SubElement(root.find('info').find('authors'), 'author')
    author.text = str(user_id)
    SaveXMLFile(user_id, pack_name, tree)


def DeletePack(chat_id, user_id, pack_name):
    """Delete pack files."""
    shutil.rmtree(os.path.join(packs_directory, str(user_id), pack_name))


def GetUserPacks(chat_id, user_id):
    """Get all the user packs names."""
    dir_content = os.listdir(os.path.join(packs_directory, str(user_id)))
    return [p for p in dir_content if
            os.path.isdir(os.path.join(packs_directory, str(user_id), p))]


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
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    rounds = root.find('rounds')
    round_to_delete = rounds.find(f"./round[@name='{round_name}']")
    rs.set_data(chat_id, user_id, 'round', round_name)
    for theme in GetThemes(chat_id, user_id):
        DeleteTheme(chat_id, user_id, theme)
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
    rs.set_data(chat_id, user_id, 'theme', theme_name)
    for q_info in GetQuestions(chat_id, user_id):
        DeleteQuestion(chat_id, user_id, q_info[0])
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
    pack_dir = os.path.join(packs_directory, str(user_id), pack_name)
    for atom in question.find('scenario').findall('atom'):
        if atom.get('type') == 'image':
            image_name = atom.text[1:]
            os.remove(os.path.join(pack_dir, 'Images', image_name))
        if atom.get('type') == 'voice':
            voice_name = atom.text[1:]
            os.remove(os.path.join(pack_dir, 'Audio', voice_name))
        if atom.get('type') == 'video':
            video_name = atom.text[1:]
            os.remove(os.path.join(pack_dir, 'Video', video_name))
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


def GetQuestionPrice(chat_id, user_id):
    """Get question price."""
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
    return question.get('price')


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


def GetQuestionAnswer(chat_id, user_id):
    """Get question answer."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    theme_name = rs.get_value(chat_id, user_id, 'theme')
    question_uuid = rs.get_value(chat_id, user_id, 'question')
    try:
        answer = root.find('rounds').find(
            f"round[@name='{round_name}']").find(
            'themes').find(f"theme[@name='{theme_name}']").find(
            'questions').find(
            f"question[@uuid='{question_uuid}']").find('right/answer').text
    except Exception:
        answer = None
    return answer


def SetQuestionText(chat_id, user_id, question):
    """Set question in form of text."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    theme_name = rs.get_value(chat_id, user_id, 'theme')
    question_uuid = rs.get_value(chat_id, user_id, 'question')
    scenario = root.find('rounds').find(
        f"round[@name='{round_name}']").find(
        'themes').find(f"theme[@name='{theme_name}']").find('questions').find(
        f"question[@uuid='{question_uuid}']").find('scenario')
    for q in scenario.findall('atom'):
        if q.get('type') != 'say':
            scenario.remove(q)
    question_text = ET.Element('atom')
    scenario.insert(0, question_text)
    question_text.text = question
    SaveXMLFile(user_id, pack_name, tree)


def SetQuestionFile(chat_id, user_id, file_abs_path, file_type):
    """Set question in form of file."""
    assert file_type in ['video', 'audio', 'image']
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    if file_type == 'image':
        folder_name = 'Images'
    elif file_type == 'audio':
        folder_name = 'Audio'
    else:
        folder_name = 'Video'
    path_to_files_folder = os.path.join(packs_directory, str(user_id),
                                        pack_name, folder_name)
    if not os.path.exists(path_to_files_folder):
        os.makedirs(path_to_files_folder)
    file_uuid = str(uuid.uuid4())
    file_format = file_abs_path.split('.')[-1]
    shutil.move(file_abs_path, os.path.join(path_to_files_folder,
                                            file_uuid + '.' + file_format))
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    theme_name = rs.get_value(chat_id, user_id, 'theme')
    question_uuid = rs.get_value(chat_id, user_id, 'question')
    scenario = root.find('rounds').find(
        f"round[@name='{round_name}']").find(
        'themes').find(f"theme[@name='{theme_name}']").find('questions').find(
        f"question[@uuid='{question_uuid}']").find('scenario')
    for q in scenario.findall('atom'):
        if q.get('type') != 'say':
            scenario.remove(q)
    question_file = ET.Element('atom')
    scenario.insert(0, question_file)
    if file_type == 'image':
        question_file.set('type', 'image')
    elif file_type == 'audio':
        question_file.set('type', 'voice')
    else:
        question_file.set('type', 'video')
    question_file.text = '@' + file_uuid + '.' + file_format
    SaveXMLFile(user_id, pack_name, tree)


def GetQuestionForm(chat_id, user_id):
    """
    Get question form.

    Returns (None, None) if there is no question,
    (text, 'text') if it is text or
    (path_to_file, 'file') if it is video, voice or image.
    """
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    theme_name = rs.get_value(chat_id, user_id, 'theme')
    question_uuid = rs.get_value(chat_id, user_id, 'question')
    scenario = root.find('rounds').find(
        f"round[@name='{round_name}']").find(
        'themes').find(f"theme[@name='{theme_name}']").find('questions').find(
        f"question[@uuid='{question_uuid}']").find('scenario')
    res = None
    q_type = None
    for atom in scenario.findall('atom'):
        if atom.get('type') != 'say':
            if atom.get('type') is None:
                res = atom.text
                q_type = 'text'
            else:
                q_type = 'file'
                assert atom.get('type') in ['image', 'voice', 'video']
                folders_names = {'image': 'Images',
                                 'voice': 'Audio',
                                 'video': 'Video'}
                res = os.path.join(packs_directory, str(user_id),
                                   pack_name, folders_names[atom.get('type')],
                                   atom.text[1:])
    return (res, q_type)


def SetQuestionType(chat_id, user_id, q_type, new_theme=None, new_cost=None):
    """Set question type."""
    assert q_type in ['usual', 'cat', 'risk']
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
    old_type_tag = question.find('type')
    if old_type_tag is not None:
        question.remove(old_type_tag)
    if q_type == 'usual':
        return
    type_tag = ET.Element('atom')
    question.insert(0, type_tag)
    if q_type == 'risk':
        type_tag.set('name', 'sponsored')
    else:
        type_tag.set('name', 'bagcat')
        theme_tag = ET.SubElement(type_tag, 'param')
        theme_tag.set('name', 'theme')
        theme_tag.text = new_theme
        cost_tag = ET.SubElement(type_tag, 'param')
        cost_tag.set('name', 'cost')
        cost_tag.text = str(new_cost)
        self_tag = ET.SubElement(type_tag, 'param')
        self_tag.set('name', 'self')
        self_tag.text = 'false'
        knows_tag = ET.SubElement(type_tag, 'param')
        knows_tag.set('name', 'knows')
        knows_tag.text = 'after'
    SaveXMLFile(user_id, pack_name, tree)


def GetQuestionType(chat_id, user_id):
    """
    Get question type.

    Returns dictionary with key 'type'. Value can be
    'usual', 'risk', 'cat' (if cat there are also keys
    'cost' and 'theme').
    """
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
    if question.get('type') is None:
        return {'type': 'usual'}
    type_tag = question.find('type')
    if type_tag.get('name') == 'sponsored':
        return {'type': 'risk'}
    new_theme = type_tag.find("param[@name='theme']").text
    new_cost = type_tag.find("param[@name='cost']").text
    return {'type': 'cat', 'cost': new_cost, 'theme': new_theme}


def SetQuestionComment(chat_id, user_id, comment_text):
    """Set question comment."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    theme_name = rs.get_value(chat_id, user_id, 'theme')
    question_uuid = rs.get_value(chat_id, user_id, 'question')
    scenario = root.find('rounds').find(
        f"round[@name='{round_name}']").find(
        'themes').find(f"theme[@name='{theme_name}']").find('questions').find(
        f"question[@uuid='{question_uuid}']").find('scenario')
    if scenario.find("atom[@type='say']") is None:
        scenario.append(ET.Element('atom', {'type': 'say'}))
    comment = scenario.find("atom[@type='say']")
    comment.text = comment_text
    SaveXMLFile(user_id, pack_name, tree)


def GetQuestionComment(chat_id, user_id):
    """Get question comment. Returns None or comment text."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    theme_name = rs.get_value(chat_id, user_id, 'theme')
    question_uuid = rs.get_value(chat_id, user_id, 'question')
    scenario = root.find('rounds').find(
        f"round[@name='{round_name}']").find(
        'themes').find(f"theme[@name='{theme_name}']").find('questions').find(
        f"question[@uuid='{question_uuid}']").find('scenario')
    if scenario.find("atom[@type='say']") is None:
        return None
    return scenario.find("atom[@type='say']").text


def DeleteQuestionComment(chat_id, user_id):
    """Delete question comment."""
    rs = CreateRedisStorage()
    pack_name = rs.get_value(chat_id, user_id, 'pack')
    tree, root = GetFileTree(user_id, pack_name)
    round_name = rs.get_value(chat_id, user_id, 'round')
    theme_name = rs.get_value(chat_id, user_id, 'theme')
    question_uuid = rs.get_value(chat_id, user_id, 'question')
    scenario = root.find('rounds').find(
        f"round[@name='{round_name}']").find(
        'themes').find(f"theme[@name='{theme_name}']").find('questions').find(
        f"question[@uuid='{question_uuid}']").find('scenario')
    if scenario.find("atom[@type='say']") is not None:
        scenario.remove(scenario.find("atom[@type='say']"))
    SaveXMLFile(user_id, pack_name, tree)


def LoadPackToSiq(chat_id, user_id, pack_name):
    """Load pack to .siq format and return path to it."""
    path_to_user_dir = os.path.join(packs_directory, str(user_id))
    path_to_siq = os.path.join(path_to_user_dir, pack_name + '.siq')
    path_to_dir = os.path.join(packs_directory, str(user_id), pack_name)
    if os.path.exists(path_to_siq):
        os.remove(path_to_siq)
    arc_name = shutil.make_archive(os.path.join(path_to_user_dir, pack_name),
                                   'zip', path_to_dir)
    shutil.move(os.path.join(path_to_user_dir, arc_name),
                path_to_siq)
    return path_to_siq

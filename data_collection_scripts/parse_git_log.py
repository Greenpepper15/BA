import json


def parse_git_log():
    example = open("odin_complete_2012_to_2022.log")
    git_data = dict()
    for line in example:
        if line[:2] == "--":
            _, commit_sha, commit_date, commit_author = line.split("--")
            git_data[commit_sha] = {"date": commit_date,
                                    "author": commit_author,
                                    "files_changed": []}
        elif line == "\n":
            pass
        else:
            print(line)
            lines_added, lines_deleted, file_name = line.split("\t")
            git_data[commit_sha]["files_changed"].append({"file_name": file_name,
                                                          "lines_added": lines_added,
                                                          "lines_deleted": lines_deleted})
    print(git_data)
    with open("odin_complete_2012_to_2022.json", "w") as file:
        file.write(json.dumps(git_data))


def parse_git_log_with_commit_msg():
    example = open("odin_src_2012_to_2022_with_msg.log")
    git_data = dict()
    for line in example:
        print(line)
        if line[:2] == "--":
            _, commit_sha, commit_date, commit_author, commit_msg = line.split("--", maxsplit=4)
            git_data[commit_sha] = {"date": commit_date,
                                    "author": commit_author,
                                    "msg": commit_msg,
                                    "files_changed": []}
        elif line == "\n":
            pass
        else:
            print(line)
            lines_added, lines_deleted, file_name = line.split("\t")
            git_data[commit_sha]["files_changed"].append({"file_name": file_name.replace("\n", ""),
                                                          "lines_added": lines_added,
                                                          "lines_deleted": lines_deleted})
    print(git_data)
    with open("odin_src_2012_to_2022_with_msg.json", "w") as file:
        file.write(json.dumps(git_data))

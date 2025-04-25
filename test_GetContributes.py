from GetContributes import get_contribute_main, fetch_github_repos


def test_should_send_mail():
    document = [{"git_name":"YuuuDays","time":"23:45","mail":"sample@com"}]
    assert get_contribute_main(document)



def test():
    fetch_github_repos("YuuuDays")
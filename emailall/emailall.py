import sys
import fire

from emailall.config.log import logger
from datetime import datetime
from emailall.common import utils
from emailall.modules.collect import Collect
from emailall.common.output import Output
from emailall.config import settings
import time


yellow = ''
white = ''
green = ''
blue = ''
red = ''
end = ''

version = 'v1.0'
message = white + '{' + red + version + ' #dev' + white + '}'

banner = f"""
{red}EmailALl is a powerful Emails integration tool{yellow}
 _____                _ _  ___  _ _ 
|  ___|              (_) |/ _ \| | | {message}{green}
| |__ _ __ ___   __ _ _| / /_\ \ | |
|  __| '_ ` _ \ / _` | | |  _  | | |{blue}
| |__| | | | | | (_| | | | | | | | |
\____/_| |_| |_|\__,_|_|_\_| |_/_|_|{white} By Microtao.
{end}
"""


class EmailAll(object):
    """
    EmailAll help summary page

    EmailAll is a powerful Email Collect tool

    Example:
        python3 emailall.py version
        python3 emailall.py check
        python3 emailall.py --domain example.com run
        python3 emailall.py --domains ./domains.txt run
    """

    def __init__(self, domain=None, domains=None):
        self.domain = domain    # 单条
        self.domains = domains  # 多条
        self.version = self.version # 版本信息
        self.access_internet = False    # 测试上网环境
        self.output = Output()  # 输出结果类
        print(self.domain)

    def main(self):
        if not self.access_internet:
            logger.log('ALERT', 'Because it cannot access the Internet')
        if self.access_internet:
            collect = Collect(self.domain)
            collect.run()
            utils.save_all(self.domain)
            settings.emails.clear()
    def run(self):
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[*] Starting EmailAll @ {dt}\n')
        logger.log('DEBUG', f'[*] Starting EmailAll @ {dt}\n')
        self.access_internet, self.in_china = utils.get_net_env()
        self.domains = utils.get_domains(self.domain, self.domains)
        count = len(self.domains)
        
        if not count:
            logger.log('FATAL', 'Failed to obtain domain')
            # sys.exit(1)
            pass
        for domain in self.domains:
            self.domain = domain
            self.main()
        time.sleep(2)
        email_result = {}
        for i in range(int(len(self.domains))):
            data = self.output.run(self.domains[i])
            email_result["email"] = data
            try:
                email_result["other"] = str(settings.rule_func[i])
            except:
                email_result["other"] = ""
        return email_result
    @staticmethod
    def version():
        """
        Print version information and exit
        """
        print(banner)
        # sys.exit(0)
        pass


if __name__ == '__main__':
    fire.Fire(EmailAll)

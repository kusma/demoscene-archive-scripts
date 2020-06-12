import argparse
import datetime
import email.utils
import hashlib
import os
import shutil
import slugify
import subprocess
import time
import urllib.parse
import urllib.request
import zipfile

parser = argparse.ArgumentParser(description='Convert Fizzer\'s source code from zip-archives to git-repos')
parser.add_argument('outdir', help='output directory')
args = parser.parse_args()

prods = [
    'The Real Party Is In Your Pocket',
    'Alive Here Now, Forever',
    'Blitzgewitter',
    'Blue Morpho',
    'Decay',
    'Dropletia',
    'Emerge',
    'From The Seas To The Stars',
    'Glittermorphosis',
    'Horizon Machine',
    'IIII  IV',
    'Love Reaction',
    'Ohanami',
    'Oscar\'s Chair',
    'RCM Invitro 2013',
    'Takochu Kiss',
    'Terrarium',
    'The Real Party Is In Your Pocket'
]

try:
    zip_dir = os.path.join(args.outdir, 'zips')
    if not os.path.isdir(zip_dir):
        os.makedirs(zip_dir)

    cwd = os.getcwd()
    for prod in prods:
        slug = slugify.slugify(prod)
        repo_dir = os.path.join(args.outdir, 'repos', slug)
        if not os.path.isdir(repo_dir):
            print('Creating repo: {0}...'.format(slug))
            subprocess.run(['git', 'init', repo_dir])

            desc = open(os.path.join(repo_dir, '.git', 'description'), 'w')
            desc.write('"{0}" by Fizzer'.format(prod))
            desc.close()

            url = 'http://amietia.com/DemoSources/{0}.zip'.format(urllib.parse.quote(prod))
            zip_path = os.path.join(args.outdir, 'zips', '{0}.zip'.format(prod))
            if not os.path.isfile(zip_path):
                print('Downloading zip: {0}...'.format(url))
                headers = urllib.request.urlretrieve(url, zip_path)[1]
                date = headers['Last-Modified']
                date = email.utils.parsedate(date)
                date = datetime.datetime(*date[:6])
                timestamp = time.mktime(date.timetuple())
                os.utime(zip_path, (timestamp, timestamp))

            prod_dir = os.path.join(args.outdir, 'tmp', slug)
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(prod_dir)

            shutil.copytree(os.path.join(prod_dir, prod), repo_dir, dirs_exist_ok=True)

            hash_md5 = hashlib.md5()
            with open(zip_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            md5 = hash_md5.hexdigest()

            date = os.path.getmtime(zip_path)
            date = '{0} +0000'.format(date)

            msg = 'initial commit\n\nimported from:\n{0}\nmd5sum: {1}'.format(url, md5)
            os.chdir(repo_dir)
            subprocess.run(['git', '-c', 'core.autocrlf=input', 'add', '.'])
            subprocess.run(['git', 'commit',
                            '--author="Edd Biddulph <eddbiddulph@gmail.com>"',
                            '--date', date,
                            '-m', msg])

            os.chdir(cwd)

finally:
    os.chdir(cwd)

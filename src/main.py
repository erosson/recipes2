import os
import string
import shutil
import urllib
import html
from recipe_grid.markdown import compile_markdown
from typing import *
from dataclasses import dataclass


@dataclass
class RecipePath:
    srcdir: str
    destdir: str
    srcpath: str
    srcfile: str

    @property
    def basename(self) -> str:
        return os.path.splitext(self.srcfile)[0]

    @property
    def src(self) -> str:
        return os.path.join(self.srcpath, self.srcfile)

    @property
    def destpath(self) -> str:
        return self.srcpath.replace(self.srcdir, self.destdir)

    @property
    def dest(self) -> str:
        return os.path.join(self.destpath, self.basename+'.html')

    @property
    def webpath(self) -> str:
        return self.srcpath.replace(self.srcdir, '')

    @property
    def web(self) -> str:
        return os.path.join(self.webpath, self.basename+'.html')


def paths(srcdir: str, destdir: str) -> Iterable[RecipePath]:
    for (srcpath, dirnames, filenames) in os.walk(srcdir):
        for f in filenames:
            if f.endswith('.md'):
                yield RecipePath(srcpath=srcpath, srcfile=f, srcdir=srcdir, destdir=destdir)


def render_recipes(paths: Iterable[RecipePath], template: str) -> Iterable[Tuple[RecipePath, str]]:
    with open(template, 'r') as fd:
        template: string.Template = string.Template(fd.read())

    for path in paths:
        with open(path.src, 'r') as fd:
            txt = fd.read()
        parsed = compile_markdown(txt)
        body = parsed.render()
        html = template.substitute(body=body, title=parsed.title)
        with open(path.dest, 'w') as fd:
            fd.write(html)

        yield (path, parsed.title)


def render_index(dest: str, titles: Iterable[Tuple[str, str]], template: str) -> None:
    with open(template, 'r') as fd:
        template: string.Template = string.Template(fd.read())

    entries = [
        f'<li><a href="/{urllib.parse.quote(path.web)}">{html.escape(title)}</a></li>'
        for (path, title) in titles]

    body = "\n".join(entries)
    html_ = template.substitute(body=body)
    with open(dest, 'w') as fd:
        fd.write(html_)


def main(srcdir: str, destdir: str, pubdir: str, templatedir: str) -> None:
    try:
        shutil.rmtree(destdir)
    except FileNotFoundError:
        pass
    shutil.copytree(pubdir, destdir)

    ps = list(paths(srcdir, destdir))
    titles = render_recipes(
        paths=ps,
        template=os.path.join(templatedir, 'recipe.html'),
    )

    render_index(
        dest=os.path.join(destdir, 'index.html'),
        titles=titles,
        template=os.path.join(templatedir, 'index.html'),
    )


if __name__ == '__main__':
    main(
        srcdir='./recipes',
        destdir='./dist',
        pubdir='./public',
        templatedir='./src',
    )

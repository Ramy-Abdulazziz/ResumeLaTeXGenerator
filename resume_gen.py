from jinja2 import Environment, FileSystemLoader, select_autoescape
import argparse
import os
import shutil
import subprocess
import glob


class ResumePDFGenerator:
    def __init__(self, tex_dir, parent_dir, save_to_desktop):
        self.directory = tex_dir
        self.parent_dir = parent_dir
        self.desktop = save_to_desktop

    def compile_latex(self):
        try:
            subprocess.run(
                ["pdflatex", self.directory],
                cwd=self.parent_dir,
                check=True,
                text=True,
                capture_output=True,
                timeout=30,
            )
            pdf_fname = os.path.basename(self.directory).replace(".tex", ".pdf")
            pdf_src_path = os.path.join(self.parent_dir, pdf_fname)
            print(f"LaTeX compiled successfully and PDF generated in directory {pdf_src_path}")
            if self.desktop:
                print("Copying pdf to desktop")
                desktop_path = os.path.join(
                    os.path.expanduser("~"), "OneDrive", "Desktop"
                )
                pdf_dest_path = os.path.join(desktop_path, pdf_fname)
                shutil.copy(pdf_src_path, pdf_dest_path)

        except subprocess.CalledProcessError as e:
            print(e)
            print("Unable to generate PDF Resume")
        except subprocess.TimeoutExpired:
            print("Error: pdflatex process timed out.")
            print("Unable to generate PDF Resume")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def clean_up_files(self):
        aux_extensions = [
            "*.aux",
            "*.log",
            "*.toc",
            "*.out",
            "*.fls",
            "*.fdb_latexmk",
        ]

        for ext in aux_extensions:
            files = glob.glob(os.path.join(self.parent_dir, ext))
            for file in files:
                try:
                    os.remove(file)
                except OSError as e:
                    print(f"Error deleting file {file}: {e}")


class TemplateGenerator:
    def __init__(self, projects, education, p_opts, e_opts, n_opt):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        templates_path = os.path.join(script_dir, "templates")
        self.env = Environment(
            loader=FileSystemLoader(templates_path),
            autoescape=select_autoescape(),
            comment_start_string="{##",
            comment_end_string="##}",
        )

        self.projects = projects
        self.education = education
        self.base_template = self.env.get_template(name="base.tex")
        self.p_opts = p_opts
        self.e_opts = e_opts
        self.n_opt = n_opt
        self.rendered = None
        self.rendered_directory = ""
        self.rendered_parent_dir = ""

    def gen_template(self):
        self.rendered = self.base_template.render(
            education=self.education, projects=self.projects, n_flag=self.n_opt
        )

    def get_rendered_template(self):
        self.gen_template()
        return self.rendered

    def save_rendered_template(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ed_desc = "_".join(self.e_opts)
        p_desc = "_".join(self.p_opts)
        dir_path = os.path.join(script_dir, "resumes", f"ED_{ed_desc}_P_{p_desc}")
        save_dir = os.path.join(dir_path, "Ramy_Abdulazziz_Resume.tex")
        self.rendered_directory = os.path.abspath(save_dir)
        self.rendered_parent_dir = os.path.abspath(dir_path)

        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

        os.makedirs(dir_path, exist_ok=True)
        with open(save_dir, "w") as file:
            file.write(self.rendered)

    def get_rendered_directory(self):
        return self.rendered_directory

    def get_rendered_parent_dir(self):
        return self.rendered_parent_dir


class TemplateArgRetriever:
    def __init__(self, selected_projects, selected_education):
        self.projects = selected_projects
        self.education = selected_education
        self.proj_list = set()
        self.ed_list = set()

    def proj_args_to_fname(self, p_arg):
        match p_arg:
            case "c":
                return "cicaida"
            case "f":
                return "finance"
            case "k":
                return "kvm"
            case "r":
                return "ransac"
            case "s":
                return "selenium"
            case "t":
                return "timber"
            case "m":
                return "mint"

    def ed_args_to_fname(self, e_arg):
        match e_arg:
            case "s":
                return "stony"
            case "g25":
                return "georgia_25"
            case "g26":
                return "georgia_26"

    def get_proj_fnames(self):
        p_fnames = set()
        for project in self.projects:
            p_fnames.add(self.proj_args_to_fname(project))
        return p_fnames

    def get_ed_fnames(self):
        ed_fnames = set()
        for ed in self.education:
            ed_fnames.add(self.ed_args_to_fname(ed))
        return ed_fnames

    def gen_proj_list(self):
        p_fnames = self.get_proj_fnames()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for fname in p_fnames:
            fpath = os.path.join(script_dir, "projects", f"{fname}.txt")
            try:
                with open(fpath, "r") as file:
                    p_latex = file.read()
                    self.proj_list.add(p_latex)
            except:
                print(f"Error: {fname} not found in projects folder")
                return None

    def gen_ed_list(self):
        ed_fnames = self.get_ed_fnames()
        script_dir = os.path.dirname(os.path.abspath(__file__))

        for fname in ed_fnames:
            fpath = os.path.join(script_dir, "education", f"{fname}.txt")
            try:
                with open(fpath, "r") as file:
                    ed_latex = file.read()
                    self.ed_list.add(ed_latex)
            except:
                print(f"Error: {fname} not found in education folder")
                return None

    def get_projs(self):
        self.gen_proj_list()
        return self.proj_list

    def get_eds(self):
        self.gen_ed_list()
        return self.ed_list


def proj_flag_to_name(flag):
    match flag:
        case "c":
            return "cicaida"
        case "f":
            return "financial sentiment analysis"
        case "k":
            return "VM scheduling in KVM"
        case "m":
            return "MintMaps"
        case "r":
            return "Image Mosaic with Homography and Ransac"
        case "s":
            return "Automated Assignment Fetcher w) Selenium"
        case "t":
            return "Timberwolf placement"


def get_arg_lists():
    parser = argparse.ArgumentParser(
        description="Generate pdf resume from latex base file"
    )
    parser.add_argument(
        "education",
        nargs="+",
        choices=["s", "g25", "g26"],
        help="List of education to include",
    )

    projects = ["c", "f", "k", "m", "r", "s", "t"]
    for proj in projects:
        parser.add_argument(
            f"-{proj}",
            action="store_true",
            help=f"Include project {proj_flag_to_name(proj)}",
        )

    parser.add_argument(
        "-D",
        action="store_true",
        help="Copy generated PDF to desktop (overwrite other files with same name)",
    )

    parser.add_argument(
        "-N", 
        action="store_true",
        help="Adjust HPE experience for networking/devops intensive roles", 
    )

    args = parser.parse_args()

    def is_project_chosen(proj):
        return getattr(args, proj)

    p_args = list(filter(is_project_chosen, projects))
    if len(args.education) > 2:
        parser.error("Only 2 education entries max")
    if len(args.education) == 2 and len(p_args) > 2: 
        parser.error("Only 2 projects can fit on one page when both educations are added")
    if len(p_args) > 3: 
        parser.error("Max 3 projects can fit on one page")
    if len(p_args) < 2: 
        parser.error("Please add at least 2 projects")
    args.education.sort()
    return p_args, args.education, getattr(args, "D"), getattr(args, "N")


def main():
    p_opts, ed_opts, desktop, networking = get_arg_lists()
    tar = TemplateArgRetriever(p_opts, ed_opts)
    p_args = tar.get_projs()
    ed_args = tar.get_eds()
    ed_args = sorted(ed_args)
    tag = TemplateGenerator(p_args, ed_args, p_opts, ed_opts, networking)
    tag.gen_template()
    tag.save_rendered_template()

    ren_dir = tag.get_rendered_directory()
    parent_dir = tag.get_rendered_parent_dir()
    rpg = ResumePDFGenerator(ren_dir, parent_dir, desktop)
    rpg.compile_latex()
    rpg.clean_up_files()


if __name__ == "__main__":
    main()

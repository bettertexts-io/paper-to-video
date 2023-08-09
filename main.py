from manim import *
import arxiv

def manim(abstract_text):
    class AbstractScene(Scene):
        def construct(self):
            # Split the abstract into lines
            lines = abstract_text.split('\n')

            # Create a VGroup to hold the lines of text
            text_group = VGroup(*[Text(line) for line in lines])

            # Arrange the lines of text vertically
            text_group.arrange(DOWN)

            # Animate the text
            self.play(FadeIn(text_group, shift=DOWN))
            self.wait()

            # Animate each line of text individually
            for text in text_group:
                self.play(Indicate(text))
                self.wait()

            # Animate the entire group of text
            self.play(text_group.animate.scale(0.5).to_edge(UP))

            self.wait()
    AbstractScene().render()

def get_abstract(arxiv_id):
    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(search.get())
    return paper.summary

def main():
    arxiv_link = "http://arxiv.org/abs/2101.11815v1"
    arxiv_id = arxiv_link.split('/')[-1]
    abstract = get_abstract(arxiv_id)
    manim(abstract)

if __name__ == "__main__":
    main()

#generate TTS in parallele to the video
#i can work for a sf startup and live in bengaluru starting with 
#
#
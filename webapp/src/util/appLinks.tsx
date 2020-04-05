import * as React from 'react';
import { Link } from "react-router-dom";

export const renderAppLinks = (className: string) => {
    return (
        <div {...{ className }} >
            <a target="_blank" href="https://academic.oup.com/bioinformatics/article/35/13/2309/5184963">Publication</a> | <a target="_blank" href="https://www.youtube.com/watch?v=XDwK73LI9Vk">Tutorial</a> | <a target="_blank" href="https://github.com/moritzschaefer/pavooc/">GitHub</a> | <Link to="/impressum">Impressum</Link> | &copy; {new Date().getFullYear()} <a href="http://moritzs.de/blog">Moritz Schaefer</a>
        </div>
    );
}

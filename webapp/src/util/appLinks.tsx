import * as React from 'react';

export const renderAppLinks = (className: string) => {
    return (
        <div {...{ className }} >
            <a target="_blank" href="http://pavooc.io/api">API</a> | <a target="_blank" href="https://www.youtube.com/watch?v=XDwK73LI9Vk">Tutorial</a> | <a target="_blank" href="https://github.com/moritzschaefer/pavooc/">GitHub</a> | &copy; {new Date().getFullYear()} <a href="http://moritzs.de/blog">Moritz Schaefer</a>
        </div>
    );
}

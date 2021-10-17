import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import Post from './post';

class Feed extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            posts: [],
            next: "",
            url: ""
        }
    }

    componentDidMount() {
        const { url } = this.props;

        fetch(url, { credentials: 'same-origin' })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                this.setState({
                    posts: data.results,
                    next: data.next,
                    url: data.url
                })
            })
            .catch((error) => console.log(error));
    }

    render() {
        const { posts, next, url } = this.state;

        let rendered_posts = posts.map((p) => 
            <div key={p.postid.toString()}>
                <Post url={p.url} />
            </div>
        );

        return (
            <div>
                {rendered_posts}
            </div>
        );
    }
}

Feed.propTypes = {
    url: PropTypes.string.isRequired,
  };
  
  export default Feed;

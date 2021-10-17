import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';

class Post extends React.Component {
  /* Display number of image and post owner of a single post
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {  
      comments: [],
      new_comment: '',
      created: '',
      logname_likes_this: false,
      numlikes: 0,
      like_url: '',
      imgUrl: '',
      owner: '',
      ownerImgUrl: '',
      ownerShowUrl: '',
      postShowUrl: '',
      postid: 0,
      url: ''
    };
    this.handleChange = this.handleChange.bind(this);
    this.addComment = this.addComment.bind(this);
    this.doubleClickLike = this.doubleClickLike.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    // Call REST API to get the post's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          comments: data.comments,
          new_comment: "",
          created: data.created,
          logname_likes_this: data.likes.lognameLikesThis,
          numlikes: data.likes.numLikes,
          like_url: data.likes.url,
          imgUrl: data.imgUrl,
          owner: data.owner,
          ownerImgUrl: data.ownerImgUrl,
          ownerShowUrl: data.ownerShowUrl,
          postShowUrl: data.postShowUrl,
          postid: data.postid,
          url: data.url
        });
      })
      .catch((error) => console.log(error));
  };

  likeHandler(liked, likeUrl, postid) {
    if (liked) {

      const unlikePicture = {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      };

      fetch(likeUrl, unlikePicture)
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .then(() => {
          this.setState(prevState => {
            return {
              logname_likes_this: false,
              numlikes: prevState.numlikes - 1,
              like_url: null
            }
          });
        })
        .catch((error) => console.log(error));
    }
    else {
  
      const likePicture = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      };

      const req_api = "/api/v1/likes/?postid=" + postid.toString();
      fetch(req_api, likePicture)
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState(prevState => { 
            return {
              logname_likes_this: true,
              numlikes: prevState.numlikes + 1,
              like_url: data.url
            }
          });
        })
        .catch((error) => console.log(error));
    }
  };

  deleteComment(com) {

    const deleteThisOne = {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    };

    fetch(com.url, deleteThisOne)
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
      })
      .then(() => {
        this.setState(prevState => {
          let com_index = 0;
          for (let x = 0; x < prevState.comments.length; ++x) {
            if (prevState.comments[x] == com) {
              com_index = x;
              break;
            }
          }
          prevState.comments.splice(com_index, 1);
          return {
            comments: prevState.comments
          }
        });
      })
      .catch((error) => console.log(error));
  }

  deleteCommentButtonRender(com) {
    if (com.lognameOwnsThis) {
      return (
        <div>
          <button className="delete-comment-button" onClick={() => {this.deleteComment(com)} }>
            Delete
          </button>
          <br />
        </div>
      );
    }
  }

  handleChange(event) {
    this.setState({ new_comment: event.target.value });
  }

  addComment(event) {
    const newComment = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "text": this.state.new_comment })
    };

    const req_api = "/api/v1/comments/?postid=" + this.state.postid.toString();
    fetch(req_api, newComment)
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState(prevState => { 
          prevState.comments.push(data)
          return {
            comments: prevState.comments,
            new_comment: ""
          }
        });
      })
      .catch((error) => console.log(error));
    event.preventDefault();
  }

  doubleClickLike() {
    if (!this.state.logname_likes_this) {
  
      const likePicture = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      };

      const req_api = "/api/v1/likes/?postid=" + this.state.postid.toString();
      fetch(req_api, likePicture)
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState(prevState => { 
            return {
              logname_likes_this: true,
              numlikes: prevState.numlikes + 1,
              like_url: data.url
            }
          });
        })
        .catch((error) => console.log(error));
    }
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { comments, new_comment, created, logname_likes_this, 
            numlikes, like_url, imgUrl, 
            owner, ownerImgUrl, ownerShowUrl, postShowUrl,
            postid, url } = this.state;
    
    let timestamp = moment.utc(created, 'YYYY-MM-DD HH:mm:ss').fromNow();
    let ownerpic = ownerImgUrl;
    let postpic = imgUrl;
    let like_statement = numlikes.toString() + " like";

    let post_comments = comments.map((com) => 
      <div key={com.commentid.toString()}>
        <b><a href={com.ownerShowUrl}>{com.owner}</a></b> <p>{com.text}</p>

        {this.deleteCommentButtonRender(com)}

        <br />
      </div>
    );

    if (numlikes != 1) {
      like_statement += "s";
    }

    let like_button_message = "like";
    if (logname_likes_this) {
      like_button_message = "unlike";
    }

    // Render number of post image and post owner
    return (
      <div className="post">
        <div>
          <a href={ownerShowUrl}><img src={ownerpic} alt="prof-pic" /></a>
          <a href={ownerShowUrl}>{owner}</a>
          <a href={postShowUrl}>{timestamp}</a>
        </div>
  
        <img src={postpic} alt="posted-pic" onDoubleClick={this.doubleClickLike}/> <br />

        <button className="like-unlike-button" onClick={() => {this.likeHandler(logname_likes_this, like_url, postid)} }>
          {like_button_message}
        </button>

        <p>{like_statement}</p> <br />

        {post_comments}

        <br />

        <form className="comment-form" onSubmit={(event) => this.addComment(event)}>
          <input type="text" value={new_comment} onChange={this.handleChange}/>
        </form>

        <br />
  
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;

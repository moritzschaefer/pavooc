import * as React from 'react';
import { push } from 'react-router-redux';
import { connect } from 'react-redux';
import Button from 'material-ui/Button';

export interface Props {
  push: any;
}

class KnockoutList extends React.Component<Props, object> {
  render() {
    return (
      <div>
        <Button onClick={() => this.props.push('/')}>Back</Button>
      </div>
    );
  }
}

export default connect<any, Props, any>(
  () => ({}),
    (dispatch: any, ownProps: any) => ({push: (route: any) => dispatch(push(route))})
)(KnockoutList);

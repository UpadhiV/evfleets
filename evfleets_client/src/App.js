import React, { Component } from 'react';
import Form from './components/Form';

import Typography from '@material-ui/core/Typography';

import { withStyles } from "@material-ui/core/styles";
import withRoot from './withRoot';
import TableData from './components/Table';

const styles = theme => ({
  root: {
    paddingTop: theme.spacing.unit * 5,
    paddingBottom: theme.spacing.unit * 15,
  },
});




class App extends Component {

  state = {
    tableData: []
  }

  setTableData = (data) => {
    this.setState({tableData: data})
  }

  render() {
    const { classes } = this.props;

    console.log(this.state)

    return (
      <div className={classes.root}>
        <Typography variant="h1" component="h2" gutterBottom align="center">
          EV Fleets
        </Typography>
        <div style={{width: '70%', margin: '0 auto'}}>
          <Form setTableData={this.setTableData} />
        </div>
        <div style={{width: '95%', margin: '0 auto'}}>
          <TableData tabledata={this.state.tableData} />
        </div>
      </div>
    );
  }
}

export default withRoot(withStyles(styles)(App));

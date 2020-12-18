import React, { Component } from 'react';
import { withStyles } from "@material-ui/core/styles";

import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import Checkbox from '@material-ui/core/Checkbox';
import ListItemText from '@material-ui/core/ListItemText';

import axios from 'axios';
import Paper from '@material-ui/core/Paper';

import Grid from '@material-ui/core/Grid';


const styles = theme => ({
  root: {
    flexGrow: 1,
  },
  formControl: {
    margin: "0 auto",
    minWidth: 220,
    maxWidth: '100%'
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
  paper: {
    padding: theme.spacing(2),
    color: theme.palette.text.secondary,
  }
});

class Form extends Component {

  constructor(props) {
    super(props)

    this.state = {
      'city': '',
      'selectedroutes': [],

      'bus_type': '',
      'bus_cost': 0,
      'utility': 0,
      'fuel_price': 0,
      'demand_charge': 0,
      'dc_efficiency': 0.92,
      'l2_efficiency': 0.0,

      'cities': [],
      'routes': []
    }
  }

  componentDidMount() {
    axios.get('/cities')
      .then((resp) => {
        this.setState(resp.data);
      })
  }

  handleChange = (id) => {
    return (val) => {
      console.log(id, val.target.value)
      if (id === 'city') {
        axios.get("/routes/" + val.target.value)
          .then(resp => {
            this.setState({ routes: resp.data.options })
          })
      }
      this.setState({ [id]: val.target.value }, () => {
        axios.post("/tabledata", this.state)
          .then(resp => {
            this.props.setTableData(resp.data.data.filter(val => this.state.selectedroutes.includes(val.route_id)))
          })
          .catch(error => {
            console.log(this.state)
          })
      })
    }
  }

  render() {
    const { classes } = this.props;

    return (
      <div className={classes.root}>
        <Grid container spacing={10}>

          <Grid item xs={12}>
            <Paper className={classes.paper}>
              <Typography variant="h4" gutterBottom>
                1. City / Routes
              </Typography>

              <Grid container justify="center">
                <Grid item xs={6} align="center">
                  <FormControl className={classes.formControl}>
                    <InputLabel id="city-select-label">Select City</InputLabel>
                    <Select
                      labelId="city-select-label"
                      id="city-select"
                      value={this.state.city}
                      onChange={this.handleChange('city')}
                    >
                      {this.state.cities.map(city => (
                        <MenuItem key={city.value} value={city.value}>{city.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={6} align="center">
                  <FormControl className={classes.formControl}>
                    <InputLabel id="routes-select-label">Select routes to analyse</InputLabel>
                    <Select
                      labelId="routes-select-label"
                      id="routes-select"
                      multiple
                      value={this.state.selectedroutes}
                      onChange={this.handleChange('selectedroutes')}
                      input={<Input />}
                      renderValue={(selected) => selected.join(', ')}
                    >
                      {this.state.routes.map((route) => (
                        <MenuItem key={route.value} value={route.value}>
                          <Checkbox checked={this.state.selectedroutes.indexOf(route.value) > -1} />
                          <ListItemText primary={route.label} />
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

              </Grid>
            </Paper>
          </Grid>


          <Grid item xs={12}>
            <Paper className={classes.paper}>
              <Typography variant="h4" gutterBottom>
                2. Price Parameters
              </Typography>

              <Grid container justify="center">

                <Grid item xs={3} align="center">
                  <FormControl className={classes.formControl}>
                    <TextField id="numeric-bus-cost" label="Cost of Electric Bus ($)" value={this.state.bus_cost} type="number"
                      onChange={this.handleChange('bus_cost')} />
                  </FormControl>
                </Grid>

                <Grid item xs={3} align="center">
                  <FormControl className={classes.formControl}>
                    <TextField id="numeric-utility-cost" label="Utility charges ($/kWh)" value={this.state.utility} type="number"
                      onChange={this.handleChange('utility')} />
                  </FormControl>
                </Grid>

                <Grid item xs={3} align="center">
                  <FormControl className={classes.formControl}>
                    <TextField id="numeric-fuel-cost" label="Fuel price ($/gallon eq)" value={this.state.fuel_price} type="number"
                      onChange={this.handleChange('fuel_price')} />
                  </FormControl>
                </Grid>

                <Grid item xs={3} align="center">
                  <FormControl className={classes.formControl}>
                    <TextField id="numeric-demand-cost" label="Demand charge ($/kW-month)" value={this.state.demand_charge} type="number"
                      onChange={this.handleChange('demand_charge')} style={{ width: '120%' }} />
                  </FormControl>
                </Grid>

              </Grid>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Paper className={classes.paper}>
              <Typography variant="h4" gutterBottom>
                3. Vehicle Parameters
              </Typography>

              <Grid container justify="center">

                <Grid item xs={6} align="center">
                  <FormControl className={classes.formControl}>
                    <InputLabel id="routes-select-label">Select bus type</InputLabel>
                    <Select
                      labelId="routes-select-label"
                      id="routes-select"
                      value={this.state.bus_type}
                      onChange={this.handleChange('bus_type')}
                      input={<Input />}
                    >
                      {[{ 'label': '30 Feet', 'value': '30ft' }, { 'label': '40 Feet', 'value': '40ft' }, { 'label': '60 Feet', 'value': '60ft' }].map((bus) => (
                        <MenuItem key={bus.value} value={bus.value}>
                          {bus.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={6} align="center">
                  <FormControl className={classes.formControl}>
                    <TextField id="numeric-dc-efficiency" label="DC Charging efficiency (Decimal %)" value={this.state.dc_efficiency} type="number"
                      onChange={this.handleChange('dc_efficiency')} style={{ width: '120%' }} />
                  </FormControl>
                </Grid>

              </Grid>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Paper className={classes.paper}>
              <Typography variant="h4" gutterBottom>
                4. Comparisons
              </Typography>

              <Grid container justify="center">

                <Grid item xs={6} align="center">
                  <FormControl className={classes.formControl}>
                    <TextField id="numeric-tco-comp" label="TCO per route <= (%)" value={this.props.tcoComparison} type="number"
                      onChange={this.props.setTCO} />
                  </FormControl>
                </Grid>

                <Grid item xs={6} align="center">
                  <FormControl className={classes.formControl}>
                    <TextField id="numeric-emission-comp" label="Emissions <= (%)" value={this.props.emissionComparison} type="number"
                      onChange={this.props.setEmission} />
                  </FormControl>
                </Grid>

              </Grid>
            </Paper>
          </Grid>

        </Grid>
      </div>
    );
  }
}

export default withStyles(styles, { withTheme: true })(Form);

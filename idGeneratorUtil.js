const Hashids = require('hashids');
const hashIds = new Hashids();
 module.exports = {
  /**
   * Generate Unique ID by timestamp
   * 
   * @returns {String}
   */
  generateId: function () {
    return hashIds.encode(new Date().getTime());
  },
};
